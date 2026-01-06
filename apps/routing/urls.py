"""
Routing URL patterns.
"""
from django.urls import path
from . import views

app_name = 'routing'

urlpatterns = [
    # Routing rules
    path('api/<uuid:gateway_id>/rules/', views.RoutingRuleListAPIView.as_view(), name='rules_api'),
    path('api/rules/<uuid:pk>/', views.RoutingRuleDetailAPIView.as_view(), name='rule_detail_api'),
    
    # Blocked contacts
    path('api/<uuid:gateway_id>/blocked/', views.BlockedContactListAPIView.as_view(), name='blocked_contacts_api'),
    path('api/blocked/<uuid:pk>/', views.BlockedContactDetailAPIView.as_view(), name='blocked_contact_detail_api'),
    
    # Communication templates
    path('api/<uuid:gateway_id>/templates/', views.CommunicationTemplateListAPIView.as_view(), name='templates_api'),
    path('api/templates/<uuid:pk>/', views.CommunicationTemplateDetailAPIView.as_view(), name='template_detail_api'),
    
    # Utilities
    path('api/<uuid:gateway_id>/stats/', views.routing_stats, name='routing_stats'),
    path('api/<uuid:gateway_id>/test/', views.test_routing, name='test_routing'),
    path('api/<uuid:gateway_id>/block-ip/', views.block_ip_address, name='block_ip'),
    path('api/<uuid:gateway_id>/unblock/<uuid:contact_id>/', views.unblock_contact, name='unblock_contact'),
]