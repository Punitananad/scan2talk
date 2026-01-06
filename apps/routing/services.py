"""
Routing service for handling communication flow logic.
"""
import time
from datetime import datetime
from django.utils import timezone as django_timezone
from django.core.cache import cache
from .models import RoutingRule, BlockedContact, CommunicationTemplate, RoutingLog


class RoutingService:
    """
    Service class for handling routing logic and decisions.
    """
    
    def can_access_gateway(self, gateway, request):
        """Check if the gateway can be accessed."""
        if not gateway.is_active:
            return False
        
        # Check if IP is blocked
        ip_address = self.get_client_ip(request)
        if self.is_blocked(gateway, 'ip', ip_address):
            return False
        
        # Check gateway-level rate limits
        if not self.check_gateway_rate_limits(gateway, ip_address):
            return False
        
        return True
    
    def get_available_channels(self, gateway):
        """Get available communication channels for a gateway."""
        settings = getattr(gateway, 'settings', None)
        if not settings:
            return ['sms', 'whatsapp', 'ivr']  # Default channels
        
        all_channels = ['sms', 'whatsapp', 'ivr', 'email']
        preferred = settings.preferred_channels or all_channels
        blocked = settings.blocked_channels or []
        
        return [ch for ch in preferred if ch not in blocked]
    
    def can_route_request(self, gateway, channel, intent, ip_address=None, user_agent=None):
        """Check if a communication request can be routed."""
        start_time = time.time()
        
        try:
            # Check if gateway is active
            if not gateway.is_active:
                self.log_routing_decision(
                    gateway, None, channel, intent, ip_address, user_agent,
                    'blocked', [], False, 'Gateway is inactive',
                    int((time.time() - start_time) * 1000)
                )
                return False
            
            # Check blocked contacts
            if ip_address and self.is_blocked(gateway, 'ip', ip_address):
                self.log_routing_decision(
                    gateway, None, channel, intent, ip_address, user_agent,
                    'blocked', [], False, 'IP address is blocked',
                    int((time.time() - start_time) * 1000)
                )
                return False
            
            # Get applicable routing rules
            applicable_rules = self.get_applicable_rules(gateway, channel, intent)
            
            if not applicable_rules:
                self.log_routing_decision(
                    gateway, None, channel, intent, ip_address, user_agent,
                    'blocked', [], False, 'No applicable routing rules',
                    int((time.time() - start_time) * 1000)
                )
                return False
            
            # Check rate limits for the first applicable rule
            rule = applicable_rules[0]
            if not rule.check_rate_limits(ip_address):
                self.log_routing_decision(
                    gateway, rule, channel, intent, ip_address, user_agent,
                    'rate_limited', [], False, 'Rate limit exceeded',
                    int((time.time() - start_time) * 1000)
                )
                return False
            
            self.log_routing_decision(
                gateway, rule, channel, intent, ip_address, user_agent,
                'allowed', rule.forward_to_channels, True, '',
                int((time.time() - start_time) * 1000)
            )
            return True
            
        except Exception as e:
            self.log_routing_decision(
                gateway, None, channel, intent, ip_address, user_agent,
                'error', [], False, str(e),
                int((time.time() - start_time) * 1000)
            )
            return False
    
    def get_applicable_rules(self, gateway, channel, intent):
        """Get routing rules applicable to the request."""
        current_time = django_timezone.now().time()
        
        rules = RoutingRule.objects.filter(
            gateway=gateway,
            is_active=True
        ).order_by('priority', 'created_at')
        
        applicable_rules = []
        for rule in rules:
            if rule.is_applicable(channel, intent, current_time):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def is_blocked(self, gateway, block_type, value):
        """Check if a contact is blocked."""
        blocked_contacts = BlockedContact.objects.filter(
            gateway=gateway,
            block_type=block_type,
            value=value
        )
        
        for contact in blocked_contacts:
            if contact.is_active():
                return True
        
        return False
    
    def check_gateway_rate_limits(self, gateway, ip_address):
        """Check gateway-level rate limits."""
        settings = getattr(gateway, 'settings', None)
        if not settings:
            return True
        
        now = django_timezone.now()
        
        # Check hourly limit
        if settings.max_interactions_per_hour:
            hour_key = f"gateway_{gateway.id}_hour_{now.hour}_{ip_address}"
            hourly_count = cache.get(hour_key, 0)
            if hourly_count >= settings.max_interactions_per_hour:
                return False
        
        # Check daily limit
        if settings.max_interactions_per_day:
            day_key = f"gateway_{gateway.id}_day_{now.date()}_{ip_address}"
            daily_count = cache.get(day_key, 0)
            if daily_count >= settings.max_interactions_per_day:
                return False
        
        return True
    
    def increment_gateway_usage(self, gateway, ip_address):
        """Increment gateway usage counters."""
        settings = getattr(gateway, 'settings', None)
        if not settings:
            return
        
        now = django_timezone.now()
        
        # Increment hourly counter
        if settings.max_interactions_per_hour:
            hour_key = f"gateway_{gateway.id}_hour_{now.hour}_{ip_address}"
            cache.set(hour_key, cache.get(hour_key, 0) + 1, 3600)
        
        # Increment daily counter
        if settings.max_interactions_per_day:
            day_key = f"gateway_{gateway.id}_day_{now.date()}_{ip_address}"
            cache.set(day_key, cache.get(day_key, 0) + 1, 86400)
    
    def get_communication_template(self, gateway, template_type, channel, intent):
        """Get appropriate communication template."""
        templates = CommunicationTemplate.objects.filter(
            gateway=gateway,
            template_type=template_type,
            is_active=True
        )
        
        for template in templates:
            if template.is_applicable(channel, intent):
                return template
        
        return None
    
    def block_contact(self, gateway, block_type, value, reason='', expires_at=None, blocked_by=None):
        """Block a contact."""
        blocked_contact, created = BlockedContact.objects.get_or_create(
            gateway=gateway,
            block_type=block_type,
            value=value,
            defaults={
                'reason': reason,
                'expires_at': expires_at,
                'blocked_by': blocked_by
            }
        )
        
        return blocked_contact
    
    def unblock_contact(self, gateway, block_type, value):
        """Unblock a contact."""
        BlockedContact.objects.filter(
            gateway=gateway,
            block_type=block_type,
            value=value
        ).delete()
    
    def log_routing_decision(self, gateway, routing_rule, channel, intent, 
                           ip_address, user_agent, action_taken, 
                           forwarded_to_channels, success, error_message, 
                           processing_time_ms):
        """Log routing decision for analytics and debugging."""
        RoutingLog.objects.create(
            gateway=gateway,
            routing_rule=routing_rule,
            channel=channel,
            intent=intent,
            ip_address=ip_address or '0.0.0.0',
            user_agent=user_agent or '',
            action_taken=action_taken,
            forwarded_to_channels=forwarded_to_channels,
            success=success,
            error_message=error_message,
            processing_time_ms=processing_time_ms
        )
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def cleanup_expired_blocks(self):
        """Clean up expired blocked contacts."""
        BlockedContact.objects.filter(
            expires_at__lt=django_timezone.now()
        ).delete()
    
    def get_routing_stats(self, gateway, days=30):
        """Get routing statistics for a gateway."""
        from datetime import timedelta
        
        end_date = django_timezone.now()
        start_date = end_date - timedelta(days=days)
        
        logs = RoutingLog.objects.filter(
            gateway=gateway,
            created_at__range=[start_date, end_date]
        )
        
        total_requests = logs.count()
        successful_requests = logs.filter(success=True).count()
        blocked_requests = logs.filter(action_taken='blocked').count()
        rate_limited_requests = logs.filter(action_taken='rate_limited').count()
        
        # Channel breakdown
        channel_stats = {}
        for log in logs:
            channel = log.channel
            if channel not in channel_stats:
                channel_stats[channel] = {'total': 0, 'successful': 0}
            channel_stats[channel]['total'] += 1
            if log.success:
                channel_stats[channel]['successful'] += 1
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'blocked_requests': blocked_requests,
            'rate_limited_requests': rate_limited_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'channel_stats': channel_stats
        }