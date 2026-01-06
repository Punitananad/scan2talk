"""
Core URL patterns.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('g/<str:identifier>/', views.GatewayAccessView.as_view(), name='gateway_access'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
]