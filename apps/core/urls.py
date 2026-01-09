"""
Core URL patterns.
"""
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('g/<str:identifier>/', views.GatewayAccessView.as_view(), name='gateway_access'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    path('refund/', views.RefundPolicyView.as_view(), name='refund'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/logo.png', permanent=True)),
]