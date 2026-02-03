from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    On detail view (retrieve), includes the list of fleets owned by the user.
    On list view, fleets are not included for performance.
    """
    
    # This field is only used for detail view - we'll handle this in the viewset
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