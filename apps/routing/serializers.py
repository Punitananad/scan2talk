"""
Routing serializers for API endpoints.
"""
from rest_framework import serializers
from .models import RoutingRule, BlockedContact, CommunicationTemplate


class RoutingRuleSerializer(serializers.ModelSerializer):
    """Serializer for routing rules."""
    
    class Meta:
        model = RoutingRule
        fields = [
            'id', 'name', 'description', 'priority',
            'allowed_channels', 'allowed_intents',
            'time_window_start', 'time_window_end', 'allowed_days',
            'max_requests_per_hour', 'max_requests_per_day',
            'emergency_only', 'emergency_escalation',
            'forward_to_channels', 'auto_response_message', 'require_approval',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_priority(self, value):
        if value < 1:
            raise serializers.ValidationError("Priority must be at least 1.")
        return value
    
    def validate_allowed_channels(self, value):
        valid_channels = ['sms', 'whatsapp', 'ivr', 'email']
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"Invalid channel: {channel}")
        return value
    
    def validate_allowed_intents(self, value):
        valid_intents = ['general', 'emergency', 'complaint', 'compliment', 'business', 'support']
        for intent in value:
            if intent not in valid_intents:
                raise serializers.ValidationError(f"Invalid intent: {intent}")
        return value
    
    def validate(self, attrs):
        # Validate time window
        start_time = attrs.get('time_window_start')
        end_time = attrs.get('time_window_end')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")
        
        # Validate allowed days
        allowed_days = attrs.get('allowed_days', [])
        for day in allowed_days:
            if not isinstance(day, int) or day < 1 or day > 7:
                raise serializers.ValidationError("Allowed days must be integers between 1 and 7.")
        
        return attrs


class BlockedContactSerializer(serializers.ModelSerializer):
    """Serializer for blocked contacts."""
    
    blocked_by_email = serializers.EmailField(source='blocked_by.email', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = BlockedContact
        fields = [
            'id', 'block_type', 'value', 'reason',
            'expires_at', 'blocked_by_email', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'blocked_by_email', 'is_active', 'created_at']
    
    def get_is_active(self, obj):
        return obj.is_active()
    
    def validate_value(self, value):
        block_type = self.initial_data.get('block_type')
        
        if block_type == 'ip':
            # Basic IP validation
            import ipaddress
            try:
                ipaddress.ip_address(value)
            except ValueError:
                raise serializers.ValidationError("Invalid IP address format.")
        
        elif block_type == 'email':
            # Email validation
            from django.core.validators import validate_email
            try:
                validate_email(value)
            except:
                raise serializers.ValidationError("Invalid email format.")
        
        elif block_type == 'phone':
            # Basic phone validation
            if not value.startswith('+') or len(value) < 10:
                raise serializers.ValidationError("Phone number must start with + and be at least 10 characters.")
        
        return value


class CommunicationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for communication templates."""
    
    class Meta:
        model = CommunicationTemplate
        fields = [
            'id', 'template_type', 'name', 'subject', 'message',
            'channels', 'intents', 'is_active', 'send_delay_seconds',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_channels(self, value):
        valid_channels = ['sms', 'whatsapp', 'ivr', 'email']
        for channel in value:
            if channel not in valid_channels:
                raise serializers.ValidationError(f"Invalid channel: {channel}")
        return value
    
    def validate_intents(self, value):
        valid_intents = ['general', 'emergency', 'complaint', 'compliment', 'business', 'support']
        for intent in value:
            if intent not in valid_intents:
                raise serializers.ValidationError(f"Invalid intent: {intent}")
        return value
    
    def validate_message(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Message is too long (max 1000 characters).")
        return value


class RoutingRuleCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating routing rules."""
    
    class Meta:
        model = RoutingRule
        fields = [
            'name', 'description', 'priority',
            'allowed_channels', 'allowed_intents',
            'emergency_only', 'forward_to_channels',
            'auto_response_message'
        ]
    
    def create(self, validated_data):
        gateway = self.context['gateway']
        validated_data['gateway'] = gateway
        return super().create(validated_data)