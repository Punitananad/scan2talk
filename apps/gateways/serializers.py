"""
Gateway serializers for API endpoints.
"""
from rest_framework import serializers
from .models import Gateway, EntryPoint, GatewaySettings


class EntryPointSerializer(serializers.ModelSerializer):
    """Serializer for entry points."""
    
    access_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EntryPoint
        fields = [
            'id', 'type', 'public_identifier', 'access_url',
            'qr_code_url', 'phone_number', 'access_count',
            'last_accessed_at', 'is_active', 'created_at'
        ]
        read_only_fields = [
            'id', 'public_identifier', 'access_url', 'qr_code_url',
            'access_count', 'last_accessed_at', 'created_at'
        ]
    
    def get_access_url(self, obj):
        return obj.get_access_url()
    
    def get_qr_code_url(self, obj):
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
        return None


class GatewaySettingsSerializer(serializers.ModelSerializer):
    """Serializer for gateway settings."""
    
    class Meta:
        model = GatewaySettings
        fields = [
            'preferred_channels', 'blocked_channels',
            'available_start_time', 'available_end_time', 'timezone',
            'max_interactions_per_hour', 'max_interactions_per_day',
            'welcome_message', 'offline_message',
            'log_interactions', 'store_contact_info'
        ]


class GatewaySerializer(serializers.ModelSerializer):
    """Serializer for gateways."""
    
    entry_points = EntryPointSerializer(many=True, read_only=True)
    settings = GatewaySettingsSerializer(read_only=True)
    public_url = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    
    class Meta:
        model = Gateway
        fields = [
            'id', 'title', 'description', 'context_type',
            'location_name', 'identifier_text',
            'is_emergency_enabled', 'auto_response_enabled', 'auto_response_message',
            'total_interactions', 'last_interaction_at',
            'entry_points', 'settings', 'public_url', 'owner_email',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_interactions', 'last_interaction_at',
            'entry_points', 'settings', 'public_url', 'owner_email',
            'created_at', 'updated_at'
        ]
    
    def get_public_url(self, obj):
        return obj.get_public_url()
    
    def validate(self, attrs):
        # Check if user can create more gateways
        request = self.context.get('request')
        if request and request.user:
            if not self.instance and not request.user.can_create_gateway():
                raise serializers.ValidationError(
                    "You have reached your gateway limit. Please upgrade your plan."
                )
        return attrs
    
    def create(self, validated_data):
        # Set owner to current user
        validated_data['owner'] = self.context['request'].user
        gateway = super().create(validated_data)
        
        # Create default entry point (QR code)
        EntryPoint.objects.create(
            gateway=gateway,
            type='qr'
        )
        
        # Create default settings
        GatewaySettings.objects.create(gateway=gateway)
        
        return gateway


class GatewayCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for gateway creation."""
    
    entry_point_types = serializers.ListField(
        child=serializers.ChoiceField(choices=EntryPoint.TYPE_CHOICES),
        write_only=True,
        required=False,
        default=['qr']
    )
    
    class Meta:
        model = Gateway
        fields = [
            'title', 'description', 'context_type',
            'location_name', 'identifier_text',
            'is_emergency_enabled', 'auto_response_enabled',
            'auto_response_message', 'entry_point_types'
        ]
    
    def create(self, validated_data):
        entry_point_types = validated_data.pop('entry_point_types', ['qr'])
        validated_data['owner'] = self.context['request'].user
        
        gateway = super().create(validated_data)
        
        # Create entry points
        for entry_type in entry_point_types:
            EntryPoint.objects.create(
                gateway=gateway,
                type=entry_type
            )
        
        # Create default settings
        GatewaySettings.objects.create(gateway=gateway)
        
        return gateway


class GatewayListSerializer(serializers.ModelSerializer):
    """Simplified serializer for gateway listing."""
    
    primary_entry_point = serializers.SerializerMethodField()
    interaction_count = serializers.IntegerField(source='total_interactions')
    
    class Meta:
        model = Gateway
        fields = [
            'id', 'title', 'context_type', 'location_name',
            'primary_entry_point', 'interaction_count',
            'last_interaction_at', 'is_active', 'created_at'
        ]
    
    def get_primary_entry_point(self, obj):
        entry_point = obj.get_primary_entry_point()
        if entry_point:
            return {
                'type': entry_point.type,
                'identifier': entry_point.public_identifier,
                'access_url': entry_point.get_access_url()
            }
        return None