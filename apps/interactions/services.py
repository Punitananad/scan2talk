"""
Interaction service for handling communication sessions and logging.
"""
import uuid
import secrets
from datetime import timedelta
from django.utils import timezone as django_timezone
from django.conf import settings
from django.core.cache import cache
from .models import InteractionSession, InteractionLog, CommunicationAttempt
from apps.routing.services import RoutingService
from apps.communications.services import CommunicationService


class InteractionService:
    """
    Service class for managing communication interactions.
    """
    
    def __init__(self):
        self.routing_service = RoutingService()
        self.communication_service = CommunicationService()
    
    def initiate_communication(self, gateway, channel, message, intent, session_data):
        """
        Initiate a communication request through the gateway.
        """
        try:
            # Create interaction session
            session = self.create_session(
                gateway=gateway,
                channel=channel,
                intent=intent,
                message=message,
                session_data=session_data
            )
            
            # Create interaction log
            interaction_log = InteractionLog.objects.create(
                gateway=gateway,
                session=session,
                channel_used=channel,
                intent=intent,
                message_content=message,
                ip_address=session_data.get('ip_address', '0.0.0.0'),
                user_agent=session_data.get('user_agent', ''),
                metadata=session_data
            )
            
            # Check routing rules
            can_route = self.routing_service.can_route_request(
                gateway=gateway,
                channel=channel,
                intent=intent,
                ip_address=session_data.get('ip_address'),
                user_agent=session_data.get('user_agent')
            )
            
            if not can_route:
                # Mark as blocked
                session.mark_blocked()
                interaction_log.was_blocked = True
                interaction_log.block_reason = 'Routing rules blocked request'
                interaction_log.mark_completed(success=False, error_message='Request blocked by routing rules')
                
                return {
                    'success': False,
                    'error': 'Communication request was blocked',
                    'session_id': session.id
                }
            
            # Get applicable routing rules
            applicable_rules = self.routing_service.get_applicable_rules(gateway, channel, intent)
            
            if not applicable_rules:
                session.mark_blocked()
                interaction_log.was_blocked = True
                interaction_log.block_reason = 'No applicable routing rules'
                interaction_log.mark_completed(success=False, error_message='No routing rules found')
                
                return {
                    'success': False,
                    'error': 'No routing configuration available',
                    'session_id': session.id
                }
            
            # Use the first applicable rule
            routing_rule = applicable_rules[0]
            
            # Increment usage counters
            routing_rule.increment_usage(session_data.get('ip_address'))
            self.routing_service.increment_gateway_usage(gateway, session_data.get('ip_address'))
            
            # Send communications based on routing rule
            success = self.send_communications(
                interaction_log=interaction_log,
                routing_rule=routing_rule,
                message=message
            )
            
            if success:
                session.mark_completed()
                interaction_log.mark_completed(success=True)
                gateway.increment_interaction_count()
                
                return {
                    'success': True,
                    'message': 'Communication sent successfully',
                    'session_id': session.id,
                    'reference_id': str(interaction_log.id)
                }
            else:
                session.status = 'completed'
                session.save()
                interaction_log.mark_completed(success=False, error_message='Failed to send communication')
                
                return {
                    'success': False,
                    'error': 'Failed to send communication',
                    'session_id': session.id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
    
    def create_session(self, gateway, channel, intent, message, session_data):
        """Create a new interaction session."""
        session_token = self.generate_session_token()
        expires_at = django_timezone.now() + timedelta(seconds=settings.GATEWAY_SESSION_TIMEOUT)
        
        session = InteractionSession.objects.create(
            gateway=gateway,
            session_token=session_token,
            channel=channel,
            intent=intent,
            message=message,
            ip_address=session_data.get('ip_address', '0.0.0.0'),
            user_agent=session_data.get('user_agent', ''),
            referrer=session_data.get('referrer', ''),
            expires_at=expires_at
        )
        
        return session
    
    def generate_session_token(self):
        """Generate a unique session token."""
        while True:
            token = secrets.token_urlsafe(32)
            if not InteractionSession.objects.filter(session_token=token).exists():
                return token
    
    def send_communications(self, interaction_log, routing_rule, message):
        """Send communications based on routing rule."""
        forward_channels = routing_rule.forward_to_channels
        
        if not forward_channels:
            # Default to the original channel
            forward_channels = [interaction_log.channel_used]
        
        success = False
        
        for channel in forward_channels:
            try:
                # Get recipient for this channel
                recipient = self.get_recipient_for_channel(interaction_log.gateway, channel)
                
                if not recipient:
                    continue
                
                # Prepare message content
                final_message = self.prepare_message_content(
                    interaction_log, routing_rule, message, channel
                )
                
                # Create communication attempt
                attempt = CommunicationAttempt.objects.create(
                    interaction_log=interaction_log,
                    channel=channel,
                    recipient=recipient,
                    message_content=final_message
                )
                
                # Send through communication service
                result = self.communication_service.send_message(
                    channel=channel,
                    recipient=recipient,
                    message=final_message,
                    gateway=interaction_log.gateway
                )
                
                if result['success']:
                    attempt.mark_sent(result.get('external_id', ''))
                    attempt.provider_name = result.get('provider', '')
                    attempt.provider_response = result.get('response', {})
                    attempt.save()
                    
                    success = True
                    
                    # Update interaction log
                    interaction_log.response_sent = True
                    interaction_log.response_channel = channel
                    interaction_log.response_message = final_message
                    interaction_log.save()
                    
                else:
                    attempt.mark_failed(
                        error_code=result.get('error_code', ''),
                        error_message=result.get('error', '')
                    )
                
            except Exception as e:
                # Log the error but continue with other channels
                continue
        
        return success
    
    def get_recipient_for_channel(self, gateway, channel):
        """Get the recipient address for a specific channel."""
        owner = gateway.owner
        
        if channel == 'sms':
            return owner.get_decrypted_phone()
        elif channel == 'whatsapp':
            return owner.get_decrypted_phone()
        elif channel == 'email':
            return owner.email
        elif channel == 'ivr':
            return owner.get_decrypted_phone()
        
        return None
    
    def prepare_message_content(self, interaction_log, routing_rule, original_message, channel):
        """Prepare the final message content for sending."""
        gateway = interaction_log.gateway
        
        # Start with gateway context
        context_info = f"Gateway: {gateway.title}"
        if gateway.location_name:
            context_info += f" ({gateway.location_name})"
        
        # Add intent information
        intent_info = f"Intent: {interaction_log.intent.title()}"
        
        # Add channel information
        channel_info = f"Via: {interaction_log.channel_used.upper()}"
        
        # Combine message parts
        message_parts = [
            f"🔔 Private Communication Request",
            "",
            context_info,
            intent_info,
            channel_info,
            "",
            "Message:",
            original_message,
            "",
            f"Reference: {str(interaction_log.id)[:8]}"
        ]
        
        # Add auto-response if configured
        if routing_rule.auto_response_message:
            message_parts.extend([
                "",
                "Auto-response sent:",
                routing_rule.auto_response_message
            ])
        
        return "\n".join(message_parts)
    
    def get_session_by_token(self, session_token):
        """Get session by token."""
        try:
            return InteractionSession.objects.get(
                session_token=session_token,
                status='active'
            )
        except InteractionSession.DoesNotExist:
            return None
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        expired_sessions = InteractionSession.objects.filter(
            expires_at__lt=django_timezone.now(),
            status='active'
        )
        
        for session in expired_sessions:
            session.status = 'expired'
            session.save()
    
    def get_interaction_stats(self, gateway, days=30):
        """Get interaction statistics for a gateway."""
        from datetime import timedelta
        
        end_date = django_timezone.now()
        start_date = end_date - timedelta(days=days)
        
        interactions = InteractionLog.objects.filter(
            gateway=gateway,
            initiated_at__range=[start_date, end_date]
        )
        
        total_interactions = interactions.count()
        successful_interactions = interactions.filter(success=True).count()
        blocked_interactions = interactions.filter(was_blocked=True).count()
        
        # Channel breakdown
        channel_stats = {}
        for interaction in interactions:
            channel = interaction.channel_used
            if channel not in channel_stats:
                channel_stats[channel] = {'total': 0, 'successful': 0}
            channel_stats[channel]['total'] += 1
            if interaction.success:
                channel_stats[channel]['successful'] += 1
        
        # Intent breakdown
        intent_stats = {}
        for interaction in interactions:
            intent = interaction.intent
            if intent not in intent_stats:
                intent_stats[intent] = {'total': 0, 'successful': 0}
            intent_stats[intent]['total'] += 1
            if interaction.success:
                intent_stats[intent]['successful'] += 1
        
        # Response time stats
        completed_interactions = interactions.filter(
            duration_seconds__isnull=False
        )
        avg_response_time = None
        if completed_interactions.exists():
            total_time = sum(i.duration_seconds for i in completed_interactions)
            avg_response_time = total_time / completed_interactions.count()
        
        return {
            'total_interactions': total_interactions,
            'successful_interactions': successful_interactions,
            'blocked_interactions': blocked_interactions,
            'success_rate': (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0,
            'channel_stats': channel_stats,
            'intent_stats': intent_stats,
            'avg_response_time_seconds': avg_response_time
        }
    
    def block_interaction_source(self, interaction_log, reason=''):
        """Block the source of an interaction."""
        self.routing_service.block_contact(
            gateway=interaction_log.gateway,
            block_type='ip',
            value=interaction_log.ip_address,
            reason=reason
        )
    
    def get_recent_interactions(self, gateway, limit=50):
        """Get recent interactions for a gateway."""
        return InteractionLog.objects.filter(
            gateway=gateway
        ).select_related('session').order_by('-initiated_at')[:limit]