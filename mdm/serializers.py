from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Fleet, Device

# =============================================================================
# USERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Includes the list of fleets owned by the user.
    Password is write-only and requires a minimum of 8 characters.
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


# =============================================================================
# FLEETS
# =============================================================================

class FleetSerializer(serializers.ModelSerializer):
    """
    Serializer for Fleet model.
    
    The owner is automatically set to the authenticated user on creation.
    """
    device_count = serializers.IntegerField(source='devices.count', read_only=True)

    class Meta:
        model = Fleet
        fields = ['id', 'name', 'owner', 'device_count', 'created_at']
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


# =============================================================================
# DEVICES
# =============================================================================

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
    serial_number = serializers.UUIDField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=Device.objects.all(),
                message="A device with this serial number already exists."
            )
        ]
    )
    
    class Meta:
        model = Device
        fields = ['id', 'serial_number', 'fleet', 'os_version', 'created_at']
        read_only_fields = ['id', 'created_at']
    
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