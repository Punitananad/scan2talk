"""
SMS communication adapter using Twilio.
"""
import logging
from django.conf import settings
from .base_adapter import BaseCommunicationAdapter

logger = logging.getLogger(__name__)


class SMSAdapter(BaseCommunicationAdapter):
    """
    SMS adapter using Twilio SMS service.
    """
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
        self._client = None
    
    def get_client(self):
        """Get Twilio client instance."""
        if not self._client and self.is_configured():
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.error("Twilio library not installed. Install with: pip install twilio")
                return None
        return self._client
    
    def send_message(self, recipient, message, gateway=None):
        """Send SMS message via Twilio."""
        try:
            client = self.get_client()
            if not client:
                return {
                    'success': False,
                    'error': 'Twilio client not available',
                    'error_code': 'CLIENT_UNAVAILABLE'
                }
            
            # Format message for SMS
            formatted_message = self.format_message(message, gateway)
            
            # Send SMS
            twilio_message = client.messages.create(
                body=formatted_message,
                from_=self.from_number,
                to=recipient
            )
            
            return {
                'success': True,
                'external_id': twilio_message.sid,
                'provider': 'twilio',
                'response': {
                    'sid': twilio_message.sid,
                    'status': twilio_message.status,
                    'direction': twilio_message.direction
                }
            }
            
        except Exception as e:
            error_message = str(e)
            error_code = 'SEND_FAILED'
            
            # Parse Twilio-specific errors
            if 'Invalid phone number' in error_message:
                error_code = 'INVALID_PHONE_NUMBER'
            elif 'Insufficient funds' in error_message:
                error_code = 'INSUFFICIENT_FUNDS'
            elif 'Authentication' in error_message:
                error_code = 'AUTHENTICATION_ERROR'
            
            logger.error(f"SMS send failed: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'error_code': error_code,
                'provider': 'twilio'
            }
    
    def validate_recipient(self, recipient):
        """Validate phone number format."""
        if not recipient:
            return False
        
        # Basic phone number validation
        # Should start with + and contain only digits and spaces/dashes
        import re
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, recipient.replace(' ', '').replace('-', '')))
    
    def is_configured(self):
        """Check if Twilio is configured."""
        return bool(self.account_sid and self.auth_token and self.from_number)
    
    def format_message(self, message, gateway=None):
        """Format message for SMS (160 character limit consideration)."""
        # SMS has a 160 character limit for single messages
        # Longer messages are automatically split by Twilio
        
        if len(message) <= 160:
            return message
        
        # For longer messages, add a truncation notice
        if len(message) > 1500:  # Very long message
            return message[:1450] + "... [Message truncated due to length]"
        
        return message
    
    def test_connection(self, test_recipient=None):
        """Test Twilio connection."""
        try:
            client = self.get_client()
            if not client:
                return {
                    'success': False,
                    'error': 'Twilio client not available'
                }
            
            # Test by fetching account info
            account = client.api.accounts(self.account_sid).fetch()
            
            result = {
                'success': True,
                'message': 'Twilio connection successful',
                'account_status': account.status,
                'account_name': account.friendly_name
            }
            
            # If test recipient provided, send a test message
            if test_recipient and self.validate_recipient(test_recipient):
                test_result = self.send_message(
                    test_recipient,
                    "Test message from Gateway Platform SMS service.",
                    None
                )
                result['test_message_sent'] = test_result['success']
                if not test_result['success']:
                    result['test_error'] = test_result['error']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Twilio test failed: {str(e)}'
            }
    
    def get_message_status(self, external_id):
        """Get message delivery status from Twilio."""
        try:
            client = self.get_client()
            if not client:
                return None
            
            message = client.messages(external_id).fetch()
            return {
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }
            
        except Exception as e:
            logger.error(f"Failed to get SMS status: {str(e)}")
            return None