from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Fleet, Device


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    On detail view (retrieve), includes the list of fleets owned by the user.
    On list view, fleets are not included for performance.
    """
    
    fleets = serializers.SerializerMethodField()
    
    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=150
    )
    
    email = serializers.EmailField(required=True)
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'date_joined', 'fleets']
        read_only_fields = ['id', 'date_joined', 'fleets']
    
    def get_fleets(self, obj):
        """Return list of fleets owned by this user."""
        return [
            {'id': fleet.id, 'name': fleet.name}
            for fleet in obj.fleets.all()
        ]


class FleetSerializer(serializers.ModelSerializer):
    """
    Serializer for Fleet model.
    
    The owner is automatically set to the authenticated user on creation.
    """
    
    class Meta:
        model = Fleet
        fields = ['id', 'name', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']
    
    def validate_name(self, value):
        """
        Validate that the fleet name is unique for this owner.
        """
        request = self.context.get('request')
        if not request or not request.user:
            return value
        
        existing = Fleet.objects.filter(
            name=value,
            owner=request.user
        )
        
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError(
                "You already have a fleet with this name."
            )
        
        return value


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for Device model.
    
    Validates that the user owns the fleet when creating or updating a device.
    """
    
    fleet = serializers.PrimaryKeyRelatedField(
        queryset=Fleet.objects.all(),
        error_messages={
            'does_not_exist': 'Fleet not found or you don\'t have access to it.',
        }
    )
    
    class Meta:
        model = Device
        fields = ['id', 'serial_number', 'fleet', 'os_version', 'created_at']
        read_only_fields = ['id', 'serial_number', 'created_at']
    
    def validate_fleet(self, value):
        """
        Validate that the authenticated user owns the specified fleet.
        """
        request = self.context.get('request')
        
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        if value.owner != request.user:
            raise serializers.ValidationError(
                "Fleet not found or you don't have access to it."
            )
        
        return value