"""
Communication views and API endpoints.
"""
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from .services import CommunicationService


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def communication_status(request):
    """Get status of all communication channels."""
    communication_service = CommunicationService()
    status_data = communication_service.get_channel_status()
    
    return Response({
        'channels': status_data,
        'available_channels': communication_service.get_available_channels()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='5/m', method='POST')
def test_channel(request):
    """Test a specific communication channel."""
    channel = request.data.get('channel')
    test_recipient = request.data.get('test_recipient')
    
    if not channel:
        return Response(
            {'error': 'Channel is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    communication_service = CommunicationService()
    result = communication_service.test_channel(channel, test_recipient)
    
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='POST')
def send_test_message(request):
    """Send a test message through a specific channel."""
    channel = request.data.get('channel')
    recipient = request.data.get('recipient')
    message = request.data.get('message', 'Test message from Gateway Platform')
    
    if not channel or not recipient:
        return Response(
            {'error': 'Channel and recipient are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    communication_service = CommunicationService()
    result = communication_service.send_message(
        channel=channel,
        recipient=recipient,
        message=message
    )
    
    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def channel_configuration_help(request):
    """Get help information for configuring communication channels."""
    
    help_data = {
        'sms': {
            'name': 'SMS via Twilio',
            'required_settings': [
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN',
                'TWILIO_PHONE_NUMBER'
            ],
            'setup_instructions': [
                '1. Sign up for a Twilio account at https://www.twilio.com',
                '2. Get your Account SID and Auth Token from the Twilio Console',
                '3. Purchase a phone number in the Twilio Console',
                '4. Add the credentials to your environment variables',
                '5. Test the configuration using the test endpoint'
            ],
            'documentation_url': 'https://www.twilio.com/docs/sms'
        },
        'whatsapp': {
            'name': 'WhatsApp Business API',
            'required_settings': [
                'WHATSAPP_BUSINESS_API_TOKEN',
                'WHATSAPP_BUSINESS_PHONE_ID'
            ],
            'setup_instructions': [
                '1. Apply for WhatsApp Business API access',
                '2. Set up a Facebook Business Manager account',
                '3. Create a WhatsApp Business Account',
                '4. Get your access token and phone number ID',
                '5. Add the credentials to your environment variables',
                '6. Configure webhook endpoints for message status updates'
            ],
            'documentation_url': 'https://developers.facebook.com/docs/whatsapp'
        },
        'ivr': {
            'name': 'IVR Calls via Twilio Voice',
            'required_settings': [
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN',
                'TWILIO_PHONE_NUMBER'
            ],
            'setup_instructions': [
                '1. Sign up for a Twilio account at https://www.twilio.com',
                '2. Get your Account SID and Auth Token from the Twilio Console',
                '3. Purchase a phone number with voice capabilities',
                '4. Add the credentials to your environment variables',
                '5. Test voice calls using the test endpoint'
            ],
            'documentation_url': 'https://www.twilio.com/docs/voice'
        },
        'email': {
            'name': 'Email via Django Backend',
            'required_settings': [
                'EMAIL_BACKEND',
                'DEFAULT_FROM_EMAIL',
                'EMAIL_HOST (if using SMTP)',
                'EMAIL_PORT (if using SMTP)',
                'EMAIL_HOST_USER (if using SMTP)',
                'EMAIL_HOST_PASSWORD (if using SMTP)'
            ],
            'setup_instructions': [
                '1. Choose an email service provider (Gmail, SendGrid, etc.)',
                '2. Configure Django email settings in settings.py',
                '3. Set up SMTP credentials or API keys',
                '4. Configure DEFAULT_FROM_EMAIL',
                '5. Test email sending using the test endpoint'
            ],
            'documentation_url': 'https://docs.djangoproject.com/en/4.2/topics/email/'
        }
    }
    
    return Response({
        'channels': help_data,
        'general_notes': [
            'All communication channels require proper configuration before use',
            'Test each channel after configuration to ensure it works correctly',
            'Monitor usage and costs for third-party services like Twilio',
            'Implement proper error handling and retry logic for production use',
            'Consider rate limiting and abuse prevention measures'
        ]
    })