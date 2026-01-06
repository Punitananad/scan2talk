"""
Interaction serializers for API endpoints.
"""
from rest_framework import serializers
from .models import InteractionLog, InteractionSession, CommunicationAttempt, InteractionFeedback


class InteractionSessionSerializer(serializers.ModelSerializer):
    """Serializer for interaction sessions."""
    
    gateway_title = serializers.CharField(source='gateway.title', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = InteractionSession
        fields = [
            'id', 'session_token', 'gateway_title', 'channel', 'intent',
            'message', 'ip_address', 'status', 'expires_at',
            'processed_at', 'response_sent', 'is_expired', 'created_at'
        ]
        read_only_fields = [
            'id', 'session_token', 'gateway_title', 'processed_at',
            'is_expired', 'created_at'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class CommunicationAttemptSerializer(serializers.ModelSerializer):
    """Serializer for communication attempts."""
    
    class Meta:
        model = CommunicationAttempt
        fields = [
            'id', 'channel', 'recipient', 'message_content',
            'status', 'external_id', 'sent_at', 'delivered_at',
            'failed_at', 'error_code', 'error_message',
            'retry_count', 'provider_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'sent_at', 'delivered_at', 'failed_at',
            'error_code', 'error_message', 'retry_count',
            'provider_name', 'created_at'
        ]


class InteractionLogSerializer(serializers.ModelSerializer):
    """Serializer for interaction logs."""
    
    gateway_title = serializers.CharField(source='gateway.title', read_only=True)
    session_token = serializers.CharField(source='session.session_token', read_only=True)
    communication_attempts = CommunicationAttemptSerializer(many=True, read_only=True)
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = InteractionLog
        fields = [
            'id', 'gateway_title', 'session_token', 'channel_used',
            'intent', 'message_content', 'initiated_at', 'completed_at',
            'duration_seconds', 'duration_display', 'was_blocked',
            'block_reason', 'success', 'error_message', 'ip_address',
            'response_sent', 'response_channel', 'response_message',
            'metadata', 'communication_attempts', 'created_at'
        ]
        read_only_fields = [
            'id', 'gateway_title', 'session_token', 'duration_display',
            'communication_attempts', 'created_at'
        ]
    
    def get_duration_display(self, obj):
        if obj.duration_seconds is not None:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            else:
                minutes = obj.duration_seconds // 60
                seconds = obj.duration_seconds % 60
                return f"{minutes}m {seconds}s"
        return None


class InteractionFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for interaction feedback."""
    
    interaction_id = serializers.UUIDField(source='interaction_log.id', read_only=True)
    
    class Meta:
        model = InteractionFeedback
        fields = [
            'id', 'interaction_id', 'feedback_type', 'notes',
            'blocked_contact', 'forwarded_to_support', 'created_at'
        ]
        read_only_fields = ['id', 'interaction_id', 'created_at']


class InteractionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for interaction listing."""
    
    gateway_title = serializers.CharField(source='gateway.title', read_only=True)
    duration_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = InteractionLog
        fields = [
            'id', 'gateway_title', 'channel_used', 'intent',
            'initiated_at', 'duration_display', 'status_display',
            'success', 'was_blocked', 'response_sent'
        ]
    
    def get_duration_display(self, obj):
        if obj.duration_seconds is not None:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            else:
                minutes = obj.duration_seconds // 60
                seconds = obj.duration_seconds % 60
                return f"{minutes}m {seconds}s"
        return "Pending"
    
    def get_status_display(self, obj):
        if obj.was_blocked:
            return "Blocked"
        elif obj.success:
            return "Success"
        elif obj.completed_at:
            return "Failed"
        else:
            return "Processing"


class InteractionStatsSerializer(serializers.Serializer):
    """Serializer for interaction statistics."""
    
    total_interactions = serializers.IntegerField()
    successful_interactions = serializers.IntegerField()
    blocked_interactions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    channel_stats = serializers.DictField()
    intent_stats = serializers.DictField()
    avg_response_time_seconds = serializers.FloatField(allow_null=True)