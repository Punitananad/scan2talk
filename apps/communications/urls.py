"""
Communication URL patterns.
"""
from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('api/status/', views.communication_status, name='status_api'),
    path('api/test-channel/', views.test_channel, name='test_channel_api'),
    path('api/send-test/', views.send_test_message, name='send_test_api'),
    path('api/help/', views.channel_configuration_help, name='help_api'),
]