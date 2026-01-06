"""
Email communication adapter using Django's email backend.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .base_adapter import BaseCommunicationAdapter

logger = logging.getLogger(__name__)


class EmailAdapter(BaseCommunicationAdapter):
    """
    Email adapter using Django's email backend.
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    
    def send_message(self, recipient, message, gateway=None):
        """Send email message via Django's email backend."""
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'Email backend not configured',
                    'error_code': 'NOT_CONFIGURED'
                }
            
            # Prepare email content
            subject = self.generate_subject(gateway)
            html_message = self.format_html_message(message, gateway)
            plain_message = self.format_message(message, gateway)
            
            # Send email
            success = send_mail(
                subject=subject,
                message=plain_message,
                from_email=self.from_email,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False
            )
            
            if success:
                return {
                    'success': True,
                    'external_id': None,  # Django doesn't provide message IDs
                    'provider': 'django_email',
                    'response': {
                        'subject': subject,
                        'recipient': recipient,
                        'from_email': self.from_email
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Email send failed',
                    'error_code': 'SEND_FAILED'
                }
                
        except Exception as e:
            error_message = str(e)
            error_code = 'SEND_FAILED'
            
            # Parse common email errors
            if 'Invalid email' in error_message or 'Invalid recipient' in error_message:
                error_code = 'INVALID_EMAIL'
            elif 'Authentication' in error_message:
                error_code = 'AUTHENTICATION_ERROR'
            elif 'Connection' in error_message:
                error_code = 'CONNECTION_ERROR'
            
            logger.error(f"Email send failed: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'error_code': error_code,
                'provider': 'django_email'
            }
    
    def validate_recipient(self, recipient):
        """Validate email address format."""
        if not recipient:
            return False
        
        # Basic email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, recipient))
    
    def is_configured(self):
        """Check if email backend is configured."""
        # Check if email backend is set and not the dummy backend
        return bool(
            self.email_backend and 
            self.email_backend != 'django.core.mail.backends.dummy.EmailBackend' and
            self.from_email
        )
    
    def generate_subject(self, gateway=None):
        """Generate email subject line."""
        if gateway:
            return f"Private Communication Request - {gateway.title}"
        else:
            return "Private Communication Request - Gateway Platform"
    
    def format_message(self, message, gateway=None):
        """Format message for plain text email."""
        lines = [
            "🔔 PRIVATE COMMUNICATION REQUEST",
            "=" * 40,
            ""
        ]
        
        if gateway:
            lines.extend([
                f"Gateway: {gateway.title}",
                f"Type: {gateway.get_context_type_display()}",
            ])
            
            if gateway.location_name:
                lines.append(f"Location: {gateway.location_name}")
            
            if gateway.identifier_text:
                lines.append(f"Identifier: {gateway.identifier_text}")
            
            lines.append("")
        
        lines.extend([
            "MESSAGE:",
            "-" * 20,
            message,
            "",
            "=" * 40,
            "This message was sent through Gateway Platform,",
            "a privacy-first communication routing service.",
            "",
            "To manage your gateways or block communications,",
            f"visit: https://{getattr(settings, 'PLATFORM_DOMAIN', 'localhost:8000')}/dashboard/",
        ])
        
        return "\n".join(lines)
    
    def format_html_message(self, message, gateway=None):
        """Format message for HTML email."""
        context = {
            'message': message,
            'gateway': gateway,
            'platform_domain': getattr(settings, 'PLATFORM_DOMAIN', 'localhost:8000'),
            'platform_name': getattr(settings, 'PLATFORM_NAME', 'Gateway Platform')
        }
        
        # Try to render HTML template, fall back to simple HTML
        try:
            return render_to_string('communications/email_template.html', context)
        except:
            # Fallback to simple HTML
            html_lines = [
                "<html><body>",
                "<h2>🔔 Private Communication Request</h2>",
                "<hr>",
            ]
            
            if gateway:
                html_lines.extend([
                    f"<p><strong>Gateway:</strong> {gateway.title}</p>",
                    f"<p><strong>Type:</strong> {gateway.get_context_type_display()}</p>",
                ])
                
                if gateway.location_name:
                    html_lines.append(f"<p><strong>Location:</strong> {gateway.location_name}</p>")
                
                if gateway.identifier_text:
                    html_lines.append(f"<p><strong>Identifier:</strong> {gateway.identifier_text}</p>")
            
            html_lines.extend([
                "<h3>Message:</h3>",
                f"<div style='background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007cba;'>",
                f"<p>{message.replace(chr(10), '<br>')}</p>",
                "</div>",
                "<hr>",
                "<p><small>This message was sent through Gateway Platform, a privacy-first communication routing service.</p>",
                f"<p><small>To manage your gateways, visit: <a href='https://{getattr(settings, 'PLATFORM_DOMAIN', 'localhost:8000')}/dashboard/'>Dashboard</a></small></p>",
                "</body></html>"
            ])
            
            return "".join(html_lines)
    
    def test_connection(self, test_recipient=None):
        """Test email backend connection."""
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'Email backend not configured'
                }
            
            # Test by attempting to get connection
            from django.core.mail import get_connection
            connection = get_connection()
            
            try:
                connection.open()
                connection.close()
                
                result = {
                    'success': True,
                    'message': 'Email backend connection successful',
                    'backend': self.email_backend,
                    'from_email': self.from_email
                }
                
                # If test recipient provided, send a test email
                if test_recipient and self.validate_recipient(test_recipient):
                    test_result = self.send_message(
                        test_recipient,
                        "This is a test email from Gateway Platform email service.",
                        None
                    )
                    result['test_email_sent'] = test_result['success']
                    if not test_result['success']:
                        result['test_error'] = test_result['error']
                
                return result
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Email connection test failed: {str(e)}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Email test failed: {str(e)}'
            }
    
    def send_bulk_message(self, recipients, message, gateway=None):
        """Send message to multiple recipients."""
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'Email backend not configured'
                }
            
            # Validate all recipients
            valid_recipients = [r for r in recipients if self.validate_recipient(r)]
            
            if not valid_recipients:
                return {
                    'success': False,
                    'error': 'No valid recipients provided'
                }
            
            # Prepare email content
            subject = self.generate_subject(gateway)
            html_message = self.format_html_message(message, gateway)
            plain_message = self.format_message(message, gateway)
            
            # Send bulk email
            from django.core.mail import send_mass_mail
            
            messages = [
                (subject, plain_message, self.from_email, [recipient])
                for recipient in valid_recipients
            ]
            
            sent_count = send_mass_mail(messages, fail_silently=False)
            
            return {
                'success': True,
                'sent_count': sent_count,
                'total_recipients': len(valid_recipients),
                'provider': 'django_email'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Bulk email send failed: {str(e)}'
            }