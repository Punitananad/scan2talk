"""
Gateway views and API endpoints.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from .models import Gateway, EntryPoint, GatewaySettings
from .serializers import (
    GatewaySerializer,
    GatewayCreateSerializer,
    GatewayListSerializer,
    EntryPointSerializer,
    GatewaySettingsSerializer
)


class GatewayListView(TemplateView):
    """Gateway management view."""
    template_name = 'gateways/list.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'gateways': user.gateways.filter(is_active=True).order_by('-created_at'),
            'gateway_usage': user.get_gateway_usage(),
        })
        
        return context


class GatewayDetailView(TemplateView):
    """Gateway detail view."""
    template_name = 'gateways/detail.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gateway_id = kwargs.get('gateway_id')
        
        gateway = get_object_or_404(
            Gateway.objects.select_related('settings').prefetch_related('entry_points'),
            id=gateway_id,
            owner=self.request.user
        )
        
        context.update({
            'gateway': gateway,
            'entry_points': gateway.entry_points.filter(is_active=True),
            'recent_interactions': gateway.interactions.order_by('-created_at')[:10],
        })
        
        return context


# API Views
class GatewayListAPIView(generics.ListCreateAPIView):
    """Gateway list and create API."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GatewayCreateSerializer
        return GatewayListSerializer
    
    def get_queryset(self):
        return Gateway.objects.filter(
            owner=self.request.user,
            is_active=True
        ).order_by('-created_at')
    
    @method_decorator(ratelimit(key='user', rate='10/h', method='POST'))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GatewayDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Gateway detail, update, and delete API."""
    serializer_class = GatewaySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Gateway.objects.filter(owner=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class EntryPointListAPIView(generics.ListCreateAPIView):
    """Entry point list and create API."""
    serializer_class = EntryPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        return EntryPoint.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user,
            is_active=True
        )
    
    def perform_create(self, serializer):
        gateway_id = self.kwargs.get('gateway_id')
        gateway = get_object_or_404(
            Gateway,
            id=gateway_id,
            owner=self.request.user
        )
        serializer.save(gateway=gateway)


class EntryPointDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Entry point detail, update, and delete API."""
    serializer_class = EntryPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EntryPoint.objects.filter(gateway__owner=self.request.user)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()


class GatewaySettingsAPIView(generics.RetrieveUpdateAPIView):
    """Gateway settings API."""
    serializer_class = GatewaySettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        gateway_id = self.kwargs.get('gateway_id')
        gateway = get_object_or_404(
            Gateway,
            id=gateway_id,
            owner=self.request.user
        )
        settings, created = GatewaySettings.objects.get_or_create(gateway=gateway)
        return settings


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='5/m', method='POST')
def regenerate_entry_point(request, entry_point_id):
    """Regenerate entry point identifier."""
    entry_point = get_object_or_404(
        EntryPoint,
        id=entry_point_id,
        gateway__owner=request.user
    )
    
    # Generate new identifier
    old_identifier = entry_point.public_identifier
    entry_point.public_identifier = entry_point.generate_identifier()
    entry_point.save()
    
    # Regenerate QR code if needed
    if entry_point.type == 'qr':
        entry_point.generate_qr_code()
    
    return Response({
        'message': 'Entry point regenerated successfully',
        'old_identifier': old_identifier,
        'new_identifier': entry_point.public_identifier,
        'access_url': entry_point.get_access_url()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def gateway_analytics(request, gateway_id):
    """Get gateway analytics data."""
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )
    
    # Get analytics data (last 30 days)
    from django.utils import timezone as django_timezone
    from datetime import timedelta
    
    end_date = django_timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    analytics = gateway.analytics.filter(
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Aggregate data
    total_interactions = sum(a.total_interactions for a in analytics)
    successful_interactions = sum(a.successful_interactions for a in analytics)
    blocked_interactions = sum(a.blocked_interactions for a in analytics)
    
    # Channel breakdown
    channel_data = {
        'sms': sum(a.sms_interactions for a in analytics),
        'whatsapp': sum(a.whatsapp_interactions for a in analytics),
        'ivr': sum(a.ivr_interactions for a in analytics),
    }
    
    # Daily data for charts
    daily_data = [
        {
            'date': a.date.isoformat(),
            'interactions': a.total_interactions,
            'successful': a.successful_interactions,
            'blocked': a.blocked_interactions
        }
        for a in analytics
    ]
    
    return Response({
        'gateway_id': gateway_id,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': {
            'total_interactions': total_interactions,
            'successful_interactions': successful_interactions,
            'blocked_interactions': blocked_interactions,
            'success_rate': (successful_interactions / total_interactions * 100) if total_interactions > 0 else 0
        },
        'channels': channel_data,
        'daily_data': daily_data
    })