"""
WhatsApp communication adapter using WhatsApp Business API.
"""
import logging
import requests
from django.conf import settings
from .base_adapter import BaseCommunicationAdapter

logger = logging.getLogger(__name__)


class WhatsAppAdapter(BaseCommunicationAdapter):
    """
    WhatsApp adapter using WhatsApp Business API.
    """
    
    def __init__(self):
        self.access_token = getattr(settings, 'WHATSAPP_BUSINESS_API_TOKEN', '')
        self.phone_number_id = getattr(settings, 'WHATSAPP_BUSINESS_PHONE_ID', '')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def send_message(self, recipient, message, gateway=None):
        """Send WhatsApp message via Business API."""
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'WhatsApp Business API not configured',
                    'error_code': 'NOT_CONFIGURED'
                }
            
            # Format message for WhatsApp
            formatted_message = self.format_message(message, gateway)
            
            # Prepare API request
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # WhatsApp message payload
            payload = {
                'messaging_product': 'whatsapp',
                'to': recipient,
                'type': 'text',
                'text': {
                    'body': formatted_message
                }
            }
            
            # Send request
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and 'messages' in response_data:
                message_id = response_data['messages'][0]['id']
                return {
                    'success': True,
                    'external_id': message_id,
                    'provider': 'whatsapp_business',
                    'response': response_data
                }
            else:
                error_message = response_data.get('error', {}).get('message', 'Unknown error')
                error_code = response_data.get('error', {}).get('code', 'UNKNOWN')
                
                return {
                    'success': False,
                    'error': error_message,
                    'error_code': error_code,
                    'provider': 'whatsapp_business',
                    'response': response_data
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'WhatsApp API request timeout',
                'error_code': 'TIMEOUT'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'WhatsApp API request failed: {str(e)}',
                'error_code': 'REQUEST_FAILED'
            }
        except Exception as e:
            logger.error(f"WhatsApp send failed: {str(e)}")
            return {
                'success': False,
                'error': f'WhatsApp send error: {str(e)}',
                'error_code': 'SEND_FAILED'
            }
    
    def validate_recipient(self, recipient):
        """Validate WhatsApp phone number format."""
        if not recipient:
            return False
        
        # WhatsApp uses E.164 format without + prefix for API
        # But we accept + prefix and remove it
        phone = recipient.replace('+', '').replace(' ', '').replace('-', '')
        
        # Should be 10-15 digits
        import re
        pattern = r'^\d{10,15}$'
        return bool(re.match(pattern, phone))
    
    def is_configured(self):
        """Check if WhatsApp Business API is configured."""
        return bool(self.access_token and self.phone_number_id)
    
    def format_message(self, message, gateway=None):
        """Format message for WhatsApp."""
        # WhatsApp supports up to 4096 characters
        if len(message) > 4000:
            return message[:3950] + "... [Message truncated due to length]"
        
        return message
    
    def test_connection(self, test_recipient=None):
        """Test WhatsApp Business API connection."""
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'WhatsApp Business API not configured'
                }
            
            # Test by fetching phone number info
            url = f"{self.base_url}/{self.phone_number_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'success': True,
                    'message': 'WhatsApp Business API connection successful',
                    'phone_number': data.get('display_phone_number', 'Unknown'),
                    'verified_name': data.get('verified_name', 'Unknown')
                }
                
                # If test recipient provided, send a test message
                if test_recipient and self.validate_recipient(test_recipient):
                    test_result = self.send_message(
                        test_recipient,
                        "Test message from Gateway Platform WhatsApp service.",
                        None
                    )
                    result['test_message_sent'] = test_result['success']
                    if not test_result['success']:
                        result['test_error'] = test_result['error']
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'WhatsApp API test failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'WhatsApp test failed: {str(e)}'
            }
    
    def send_template_message(self, recipient, template_name, template_params=None):
        """
        Send a WhatsApp template message.
        Template messages are required for initiating conversations.
        """
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'WhatsApp Business API not configured'
                }
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': recipient,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': 'en'
                    }
                }
            }
            
            # Add template parameters if provided
            if template_params:
                payload['template']['components'] = [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': param}
                            for param in template_params
                        ]
                    }
                ]
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and 'messages' in response_data:
                return {
                    'success': True,
                    'external_id': response_data['messages'][0]['id'],
                    'provider': 'whatsapp_business',
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Template send failed'),
                    'error_code': response_data.get('error', {}).get('code', 'TEMPLATE_FAILED')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Template message failed: {str(e)}',
                'error_code': 'TEMPLATE_ERROR'
            }
    
    def get_message_status(self, external_id):
        """Get message delivery status from WhatsApp Business API."""
        # Note: WhatsApp Business API provides webhook notifications for status updates
        # This method would typically query a local database of webhook data
        # For now, return None as status tracking requires webhook implementation
        return None