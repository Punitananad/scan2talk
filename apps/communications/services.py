"""
Communication service for handling different messaging channels.
"""
import logging
from abc import ABC, abstractmethod
from django.conf import settings
from .adapters.sms_adapter import SMSAdapter
from .adapters.whatsapp_adapter import WhatsAppAdapter
from .adapters.ivr_adapter import IVRAdapter
from .adapters.email_adapter import EmailAdapter

logger = logging.getLogger(__name__)


class CommunicationService:
    """
    Main service for handling communications across different channels.
    """
    
    def __init__(self):
        self.adapters = {
            'sms': SMSAdapter(),
            'whatsapp': WhatsAppAdapter(),
            'ivr': IVRAdapter(),
            'email': EmailAdapter(),
        }
    
    def send_message(self, channel, recipient, message, gateway=None):
        """
        Send a message through the specified channel.
        
        Args:
            channel (str): Communication channel ('sms', 'whatsapp', 'ivr', 'email')
            recipient (str): Recipient address (phone, email, etc.)
            message (str): Message content
            gateway (Gateway): Gateway instance for context
            
        Returns:
            dict: Result with success status and details
        """
        try:
            if channel not in self.adapters:
                return {
                    'success': False,
                    'error': f'Unsupported channel: {channel}',
                    'error_code': 'UNSUPPORTED_CHANNEL'
                }
            
            adapter = self.adapters[channel]
            
            # Validate recipient for the channel
            if not adapter.validate_recipient(recipient):
                return {
                    'success': False,
                    'error': f'Invalid recipient for {channel}: {recipient}',
                    'error_code': 'INVALID_RECIPIENT'
                }
            
            # Send the message
            result = adapter.send_message(recipient, message, gateway)
            
            # Log the attempt
            logger.info(
                f"Communication attempt - Channel: {channel}, "
                f"Recipient: {recipient[:5]}..., Success: {result['success']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Communication error - Channel: {channel}, Error: {str(e)}")
            return {
                'success': False,
                'error': f'Communication service error: {str(e)}',
                'error_code': 'SERVICE_ERROR'
            }
    
    def get_available_channels(self):
        """Get list of available communication channels."""
        available = []
        
        for channel, adapter in self.adapters.items():
            if adapter.is_configured():
                available.append(channel)
        
        return available
    
    def test_channel(self, channel, test_recipient=None):
        """
        Test a communication channel configuration.
        
        Args:
            channel (str): Channel to test
            test_recipient (str): Optional test recipient
            
        Returns:
            dict: Test result
        """
        try:
            if channel not in self.adapters:
                return {
                    'success': False,
                    'error': f'Unknown channel: {channel}'
                }
            
            adapter = self.adapters[channel]
            
            # Check if adapter is configured
            if not adapter.is_configured():
                return {
                    'success': False,
                    'error': f'{channel} adapter is not configured'
                }
            
            # Run adapter-specific test
            return adapter.test_connection(test_recipient)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Test failed: {str(e)}'
            }
    
    def get_channel_status(self):
        """Get status of all communication channels."""
        status = {}
        
        for channel, adapter in self.adapters.items():
            try:
                status[channel] = {
                    'configured': adapter.is_configured(),
                    'available': adapter.is_configured(),
                    'last_test': None  # Could be enhanced to track last test time
                }
            except Exception as e:
                status[channel] = {
                    'configured': False,
                    'available': False,
                    'error': str(e)
                }
        
        return status