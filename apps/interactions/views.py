"""
Interaction views and API endpoints.
"""
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from apps.gateways.models import Gateway
from .models import InteractionLog, InteractionSession, InteractionFeedback
from .serializers import (
    InteractionLogSerializer,
    InteractionListSerializer,
    InteractionSessionSerializer,
    InteractionFeedbackSerializer,
    InteractionStatsSerializer
)
from .services import InteractionService


class InteractionLogListAPIView(generics.ListAPIView):
    """Interaction log list API."""
    serializer_class = InteractionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        queryset = InteractionLog.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user
        ).select_related('gateway', 'session').order_by('-initiated_at')
        
        # Filter by channel
        channel = self.request.query_params.get('channel')
        if channel:
            queryset = queryset.filter(channel_used=channel)
        
        # Filter by intent
        intent = self.request.query_params.get('intent')
        if intent:
            queryset = queryset.filter(intent=intent)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter == 'success':
            queryset = queryset.filter(success=True, was_blocked=False)
        elif status_filter == 'blocked':
            queryset = queryset.filter(was_blocked=True)
        elif status_filter == 'failed':
            queryset = queryset.filter(success=False, was_blocked=False)
        
        return queryset


class InteractionLogDetailAPIView(generics.RetrieveAPIView):
    """Interaction log detail API."""
    serializer_class = InteractionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return InteractionLog.objects.filter(
            gateway__owner=self.request.user
        ).select_related('gateway', 'session').prefetch_related('communication_attempts')


class InteractionSessionListAPIView(generics.ListAPIView):
    """Interaction session list API."""
    serializer_class = InteractionSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        return InteractionSession.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user
        ).select_related('gateway').order_by('-created_at')


class InteractionFeedbackAPIView(generics.CreateAPIView):
    """Interaction feedback API."""
    serializer_class = InteractionFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        interaction_id = self.kwargs.get('interaction_id')
        interaction_log = get_object_or_404(
            InteractionLog,
            id=interaction_id,
            gateway__owner=self.request.user
        )
        
        feedback = serializer.save(interaction_log=interaction_log)
        
        # Handle feedback actions
        if feedback.blocked_contact:
            interaction_service = InteractionService()
            interaction_service.block_interaction_source(
                interaction_log=interaction_log,
                reason=f"Blocked due to feedback: {feedback.feedback_type}"
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def interaction_stats(request, gateway_id):
    """Get interaction statistics for a gateway."""
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )
    
    days = int(request.query_params.get('days', 30))
    if days > 365:
        days = 365
    
    interaction_service = InteractionService()
    stats = interaction_service.get_interaction_stats(gateway, days)
    
    serializer = InteractionStatsSerializer(stats)
    
    return Response({
        'gateway_id': gateway_id,
        'period_days': days,
        'stats': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def interaction_analytics(request, gateway_id):
    """Get detailed interaction analytics for a gateway."""
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )
    
    days = int(request.query_params.get('days', 30))
    if days > 365:
        days = 365
    
    from datetime import timedelta
    from django.utils import timezone as django_timezone
    from django.db import models
    
    end_date = django_timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get interactions in the period
    interactions = InteractionLog.objects.filter(
        gateway=gateway,
        initiated_at__range=[start_date, end_date]
    )
    
    # Daily breakdown
    daily_stats = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        day_interactions = interactions.filter(
            initiated_at__date=current_date
        )
        
        daily_stats.append({
            'date': current_date.isoformat(),
            'total': day_interactions.count(),
            'successful': day_interactions.filter(success=True).count(),
            'blocked': day_interactions.filter(was_blocked=True).count(),
            'failed': day_interactions.filter(success=False, was_blocked=False).count()
        })
        
        current_date += timedelta(days=1)
    
    # Hourly breakdown (last 7 days)
    recent_start = end_date - timedelta(days=7)
    hourly_stats = []
    for hour in range(24):
        hour_interactions = interactions.filter(
            initiated_at__gte=recent_start,
            initiated_at__hour=hour
        )
        hourly_stats.append({
            'hour': hour,
            'count': hour_interactions.count()
        })
    
    # Channel performance
    channel_performance = interactions.values('channel_used').annotate(
        total=Count('id'),
        successful=Count('id', filter=models.Q(success=True)),
        avg_duration=Avg('duration_seconds')
    )
    
    # Intent breakdown
    intent_breakdown = interactions.values('intent').annotate(
        total=Count('id'),
        successful=Count('id', filter=models.Q(success=True))
    )
    
    # Top IP addresses
    top_ips = interactions.values('ip_address').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'gateway_id': gateway_id,
        'period': {
            'start_date': start_date.date().isoformat(),
            'end_date': end_date.date().isoformat(),
            'days': days
        },
        'daily_stats': daily_stats,
        'hourly_stats': hourly_stats,
        'channel_performance': list(channel_performance),
        'intent_breakdown': list(intent_breakdown),
        'top_ips': list(top_ips)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='POST')
def block_interaction_source(request, interaction_id):
    """Block the source of a specific interaction."""
    interaction_log = get_object_or_404(
        InteractionLog,
        id=interaction_id,
        gateway__owner=request.user
    )
    
    reason = request.data.get('reason', 'Blocked by gateway owner')
    
    interaction_service = InteractionService()
    interaction_service.block_interaction_source(
        interaction_log=interaction_log,
        reason=reason
    )
    
    return Response({
        'message': 'Source blocked successfully',
        'blocked_ip': interaction_log.ip_address
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cleanup_expired_sessions(request):
    """Cleanup expired interaction sessions."""
    interaction_service = InteractionService()
    interaction_service.cleanup_expired_sessions()
    
    return Response({
        'message': 'Expired sessions cleaned up successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_interactions(request, gateway_id):
    """Get recent interactions for a gateway."""
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )
    
    limit = int(request.query_params.get('limit', 20))
    if limit > 100:
        limit = 100
    
    interaction_service = InteractionService()
    interactions = interaction_service.get_recent_interactions(gateway, limit)
    
    serializer = InteractionListSerializer(interactions, many=True)
    
    return Response({
        'gateway_id': gateway_id,
        'interactions': serializer.data
    })