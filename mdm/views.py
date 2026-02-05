from django.contrib.auth.models import User
from rest_framework	import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Fleet, Device
from .serializers import FleetSerializer, UserSerializer, DeviceSerializer
from .permissions import IsAdminUser, IsAdminOrSelf
from drf_spectacular.utils import extend_schema, extend_schema_view


# =============================================================================
# USERS
# =============================================================================

@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Return all users. Admin only.",
    ),
    retrieve=extend_schema(
        summary="Get user details",
        description="Return user details including their fleets. Admin can view any user, "
                    "regular users can only view their own profile.",
    ),
)
class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """User management endpoints."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @extend_schema(
        summary="Create a user",
        description="Create a new user account. Admin only.",
    )
    def create(self, request, *args, **kwargs):
        """Create a new user with proper password hashing."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get my profile",
        description="Return the authenticated user's profile with their fleets.",
    )
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Return the authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [IsAdminUser()]
        elif self.action == 'retrieve':
            return [IsAdminOrSelf()]
        elif self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


# =============================================================================
# FLEETS
# =============================================================================

@extend_schema_view(
    list=extend_schema(
        summary="List fleets",
        description="Return all fleets owned by the authenticated user.",
    ),
    create=extend_schema(
        summary="Create a fleet",
        description="Create a new fleet. The owner is automatically set to the authenticated user. "
                    "Fleet names must be unique per user.",
    ),
    retrieve=extend_schema(
        summary="Get fleet details",
        description="Return details of a specific fleet owned by the authenticated user.",
    ),
)    
class FleetViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Fleet management endpoints.
    
    **Permissions:** Users can only access their own fleets.
    """
    
    serializer_class = FleetSerializer
    
    def get_queryset(self):
        """Return only fleets owned by the authenticated user."""
        return Fleet.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set the owner to the current user."""
        serializer.save(owner=self.request.user)


# =============================================================================
# DEVICES
# =============================================================================

@extend_schema_view(
    list=extend_schema(
        summary="List devices",
        description="Return all devices in fleets owned by the authenticated user.",
    ),
    create=extend_schema(
        summary="Create a device",
        description="Create a new device in a fleet owned by the authenticated user. "
                    "Serial number is auto-generated if not provided.",
    ),
    retrieve=extend_schema(
        summary="Get device details",
        description="Return details of a specific device. The device must belong to a fleet owned by the authenticated user.",
    ),
    update=extend_schema(
        summary="Update a device",
        description="Full update of a device. The device must belong to a fleet owned by the authenticated user.",
    ),
    partial_update=extend_schema(
        summary="Partial update a device",
        description="Partial update of a device. Can be used to move a device to another fleet "
                    "(the user must own both fleets).",
    ),
    destroy=extend_schema(
        summary="Delete a device",
        description="Delete a device. The device must belong to a fleet owned by the authenticated user.",
    ),
)
class DeviceViewSet(viewsets.ModelViewSet):
    """
    Device management endpoints.
    
    **Permissions:** Users can only manage devices in their own fleets.
    
    **Filtering:** Use `?fleet={id}` to filter by fleet.
    """
    
    serializer_class = DeviceSerializer
    
    def get_queryset(self):
        """
        Return only devices in fleets owned by the authenticated user.
    
        Supports filtering by fleet: GET /api/devices/?fleet=2
        """
        queryset = Device.objects.filter(fleet__owner=self.request.user)
    
        # Filter by fleet if provided
        fleet_id = self.request.query_params.get('fleet')
        if fleet_id:
            queryset = queryset.filter(fleet_id=fleet_id)
    
        return queryset
