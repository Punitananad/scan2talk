"""
IVR (Interactive Voice Response) communication adapter using Twilio Voice.
"""
import logging
from django.conf import settings
from .base_adapter import BaseCommunicationAdapter

logger = logging.getLogger(__name__)


class IVRAdapter(BaseCommunicationAdapter):
    """
    IVR adapter using Twilio Voice service for phone calls.
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
        """Initiate IVR call via Twilio Voice."""
        try:
            client = self.get_client()
            if not client:
                return {
                    'success': False,
                    'error': 'Twilio client not available',
                    'error_code': 'CLIENT_UNAVAILABLE'
                }
            
            # Generate TwiML for the call
            twiml_url = self.generate_twiml_url(message, gateway)
            
            # Initiate the call
            call = client.calls.create(
                twiml=self.generate_twiml(message, gateway),
                to=recipient,
                from_=self.from_number,
                timeout=30,  # Ring for 30 seconds
                record=False  # Don't record for privacy
            )
            
            return {
                'success': True,
                'external_id': call.sid,
                'provider': 'twilio_voice',
                'response': {
                    'sid': call.sid,
                    'status': call.status,
                    'direction': call.direction,
                    'to': call.to,
                    'from': call.from_
                }
            }
            
        except Exception as e:
            error_message = str(e)
            error_code = 'CALL_FAILED'
            
            # Parse Twilio-specific errors
            if 'Invalid phone number' in error_message:
                error_code = 'INVALID_PHONE_NUMBER'
            elif 'Insufficient funds' in error_message:
                error_code = 'INSUFFICIENT_FUNDS'
            elif 'Authentication' in error_message:
                error_code = 'AUTHENTICATION_ERROR'
            
            logger.error(f"IVR call failed: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'error_code': error_code,
                'provider': 'twilio_voice'
            }
    
    def validate_recipient(self, recipient):
        """Validate phone number format for voice calls."""
        if not recipient:
            return False
        
        # Basic phone number validation
        import re
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, recipient.replace(' ', '').replace('-', '')))
    
    def is_configured(self):
        """Check if Twilio Voice is configured."""
        return bool(self.account_sid and self.auth_token and self.from_number)
    
    def generate_twiml(self, message, gateway=None):
        """Generate TwiML for the voice call."""
        # Format message for speech
        speech_message = self.format_message_for_speech(message, gateway)
        
        # Create TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="en-US">
        Hello, you have received a private communication request through Gateway Platform.
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        {speech_message}
    </Say>
    <Pause length="2"/>
    <Say voice="alice" language="en-US">
        This message will now repeat once more.
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        {speech_message}
    </Say>
    <Pause length="1"/>
    <Say voice="alice" language="en-US">
        Thank you. Goodbye.
    </Say>
</Response>"""
        
        return twiml
    
    def format_message_for_speech(self, message, gateway=None):
        """Format message for text-to-speech."""
        # Clean up message for speech synthesis
        speech_message = message
        
        # Replace common symbols and abbreviations
        replacements = {
            '&': ' and ',
            '@': ' at ',
            '#': ' number ',
            '$': ' dollars ',
            '%': ' percent ',
            '+': ' plus ',
            '=': ' equals ',
            '<': ' less than ',
            '>': ' greater than ',
            '|': ' or ',
            '_': ' underscore ',
            '*': ' star ',
            '~': ' tilde ',
            '^': ' caret ',
            '`': ' backtick ',
            '{': ' open brace ',
            '}': ' close brace ',
            '[': ' open bracket ',
            ']': ' close bracket ',
            '(': ' open parenthesis ',
            ')': ' close parenthesis ',
        }
        
        for symbol, replacement in replacements.items():
            speech_message = speech_message.replace(symbol, replacement)
        
        # Add context if gateway is provided
        if gateway:
            context = f"This message is regarding {gateway.title}"
            if gateway.location_name:
                context += f" at {gateway.location_name}"
            speech_message = f"{context}. {speech_message}"
        
        # Limit length for voice calls (TTS has practical limits)
        if len(speech_message) > 500:
            speech_message = speech_message[:450] + "... Message truncated due to length."
        
        return speech_message
    
    def generate_twiml_url(self, message, gateway=None):
        """
        Generate a URL that serves TwiML for the call.
        In production, this would be a webhook endpoint.
        """
        # For now, return None as we're using inline TwiML
        # In production, you'd implement a webhook endpoint that serves TwiML
        return None
    
    def test_connection(self, test_recipient=None):
        """Test Twilio Voice connection."""
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
                'message': 'Twilio Voice connection successful',
                'account_status': account.status,
                'account_name': account.friendly_name
            }
            
            # If test recipient provided, initiate a test call
            if test_recipient and self.validate_recipient(test_recipient):
                test_result = self.send_message(
                    test_recipient,
                    "This is a test call from Gateway Platform IVR service.",
                    None
                )
                result['test_call_initiated'] = test_result['success']
                if not test_result['success']:
                    result['test_error'] = test_result['error']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Twilio Voice test failed: {str(e)}'
            }
    
    def get_call_status(self, external_id):
        """Get call status from Twilio."""
        try:
            client = self.get_client()
            if not client:
                return None
            
            call = client.calls(external_id).fetch()
            return {
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'answered_by': call.answered_by,
                'price': call.price,
                'price_unit': call.price_unit
            }
            
        except Exception as e:
            logger.error(f"Failed to get call status: {str(e)}")
            return None
    
    def create_conference_call(self, participants, message, gateway=None):
        """
        Create a conference call with multiple participants.
        This could be used for emergency escalation.
        """
        try:
            client = self.get_client()
            if not client:
                return {
                    'success': False,
                    'error': 'Twilio client not available'
                }
            
            conference_name = f"gateway-{gateway.id if gateway else 'emergency'}"
            calls = []
            
            # Create TwiML for conference
            conference_twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Emergency conference call initiated through Gateway Platform.
    </Say>
    <Dial>
        <Conference>{conference_name}</Conference>
    </Dial>
</Response>"""
            
            # Call each participant
            for participant in participants:
                if self.validate_recipient(participant):
                    call = client.calls.create(
                        twiml=conference_twiml,
                        to=participant,
                        from_=self.from_number
                    )
                    calls.append(call.sid)
            
            return {
                'success': True,
                'conference_name': conference_name,
                'call_sids': calls,
                'provider': 'twilio_voice'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Conference call failed: {str(e)}'
            }