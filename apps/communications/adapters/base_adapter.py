"""
Base adapter class for communication channels.
"""
from abc import ABC, abstractmethod


class BaseCommunicationAdapter(ABC):
    """
    Abstract base class for communication adapters.
    """
    
    @abstractmethod
    def send_message(self, recipient, message, gateway=None):
        """
        Send a message to the recipient.
        
        Args:
            recipient (str): Recipient address
            message (str): Message content
            gateway (Gateway): Gateway instance for context
            
        Returns:
            dict: Result with success status and details
        """
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient):
        """
        Validate recipient address format.
        
        Args:
            recipient (str): Recipient address
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def is_configured(self):
        """
        Check if the adapter is properly configured.
        
        Returns:
            bool: True if configured, False otherwise
        """
        pass
    
    def test_connection(self, test_recipient=None):
        """
        Test the connection/configuration.
        
        Args:
            test_recipient (str): Optional test recipient
            
        Returns:
            dict: Test result
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Adapter is not configured'
            }
        
        return {
            'success': True,
            'message': 'Configuration appears valid'
        }
    
    def format_message(self, message, gateway=None):
        """
        Format message for the specific channel.
        
        Args:
            message (str): Original message
            gateway (Gateway): Gateway instance for context
            
        Returns:
            str: Formatted message
        """
        return message
    
    def get_provider_name(self):
        """
        Get the name of the communication provider.
        
        Returns:
            str: Provider name
        """
        return self.__class__.__name__.replace('Adapter', '').lower()