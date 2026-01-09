"""
Routing views and API endpoints.
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit

from apps.gateways.models import Gateway
from .models import RoutingRule, BlockedContact, CommunicationTemplate
from .serializers import (
    RoutingRuleSerializer,
    RoutingRuleCreateSerializer,
    BlockedContactSerializer,
    CommunicationTemplateSerializer
)
from .services import RoutingService


class RoutingRuleListAPIView(generics.ListCreateAPIView):
    """Routing rule list and create API."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoutingRuleCreateSerializer
        return RoutingRuleSerializer

    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        return RoutingRule.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user,
            is_active=True
        ).order_by('priority', 'created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        gateway_id = self.kwargs.get('gateway_id')
        gateway = get_object_or_404(
            Gateway,
            id=gateway_id,
            owner=self.request.user
        )
        context['gateway'] = gateway
        return context


class RoutingRuleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Routing rule detail, update, and delete API."""
    serializer_class = RoutingRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RoutingRule.objects.filter(gateway__owner=self.request.user)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class BlockedContactListAPIView(generics.ListCreateAPIView):
    """Blocked contact list and create API."""
    serializer_class = BlockedContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        return BlockedContact.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        gateway_id = self.kwargs.get('gateway_id')
        gateway = get_object_or_404(
            Gateway,
            id=gateway_id,
            owner=self.request.user
        )
        serializer.save(
            gateway=gateway,
            blocked_by=self.request.user
        )


class BlockedContactDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Blocked contact detail, update, and delete API."""
    serializer_class = BlockedContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BlockedContact.objects.filter(gateway__owner=self.request.user)


class CommunicationTemplateListAPIView(generics.ListCreateAPIView):
    """Communication template list and create API."""
    serializer_class = CommunicationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_id')
        return CommunicationTemplate.objects.filter(
            gateway_id=gateway_id,
            gateway__owner=self.request.user
        ).order_by('template_type', 'name')

    def perform_create(self, serializer):
        gateway_id = self.kwargs.get('gateway_id')
        gateway = get_object_or_404(
            Gateway,
            id=gateway_id,
            owner=self.request.user
        )
        serializer.save(gateway=gateway)


class CommunicationTemplateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Communication template detail, update, and delete API."""
    serializer_class = CommunicationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommunicationTemplate.objects.filter(gateway__owner=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def routing_stats(request, gateway_id):
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )

    days = min(int(request.GET.get('days', 30)), 365)

    routing_service = RoutingService()
    stats = routing_service.get_routing_stats(gateway, days)

    return Response({
        'gateway_id': gateway_id,
        'period_days': days,
        'stats': stats
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='POST')
def test_routing(request, gateway_id):
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )

    channel = request.data.get('channel')
    intent = request.data.get('intent')

    if not channel or not intent:
        return Response(
            {'error': 'Channel and intent are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    routing_service = RoutingService()

    applicable_rules = routing_service.get_applicable_rules(gateway, channel, intent)
    can_route = routing_service.can_route_request(
        gateway, channel, intent,
        ip_address='127.0.0.1',
        user_agent='Test'
    )

    available_channels = routing_service.get_available_channels(gateway)
    template = routing_service.get_communication_template(
        gateway, 'auto_reply', channel, intent
    )

    return Response({
        'gateway_id': gateway_id,
        'can_route': can_route,
        'applicable_rules': [
            {
                'id': r.id,
                'name': r.name,
                'priority': r.priority,
                'forward_to_channels': r.forward_to_channels
            } for r in applicable_rules
        ],
        'available_channels': available_channels,
        'auto_response_template': {
            'name': template.name,
            'message': template.message
        } if template else None
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@ratelimit(key='user', rate='5/m', method='POST')
def block_ip_address(request, gateway_id):
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )

    ip_address = request.data.get('ip_address')
    reason = request.data.get('reason', '')

    if not ip_address:
        return Response(
            {'error': 'IP address is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    import ipaddress
    ipaddress.ip_address(ip_address)

    routing_service = RoutingService()
    blocked_contact = routing_service.block_contact(
        gateway=gateway,
        block_type='ip',
        value=ip_address,
        reason=reason,
        blocked_by=request.user
    )

    return Response({
        'message': 'IP address blocked successfully',
        'blocked_contact_id': blocked_contact.id
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unblock_contact(request, gateway_id, contact_id):
    gateway = get_object_or_404(
        Gateway,
        id=gateway_id,
        owner=request.user
    )

    blocked_contact = get_object_or_404(
        BlockedContact,
        id=contact_id,
        gateway=gateway
    )

    routing_service = RoutingService()
    routing_service.unblock_contact(
        gateway=gateway,
        block_type=blocked_contact.block_type,
        value=blocked_contact.value
    )

    return Response({'message': 'Contact unblocked successfully'})
