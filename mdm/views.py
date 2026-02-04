from django.contrib.auth.models import User
from rest_framework	import viewsets, mixins, status
from rest_framework.response import Response
from .models import Fleet, Device
from .serializers import FleetSerializer, UserSerializer, DeviceSerializer
from .permissions import IsAdminUser, IsAdminOrSelf


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing users.
    
    list:     GET /api/users/        - Admin only
    create:   POST /api/users/       - Admin only
    retrieve: GET /api/users/{id}/   - Admin or profile owner
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Return different permissions based on action:
        - list/create: Admin only
        - retrieve: Admin or self
        """
        if self.action in ['list', 'create']:
            return [IsAdminUser()]
        elif self.action == 'retrieve':
            return [IsAdminOrSelf()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user.
        
        Expects: {"username": "...", "email": "...", "password": "..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user with proper password hashing
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        # Return the created user
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    
class FleetViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing fleets.
    
    Users can only see and manage their own fleets.
    
    list:     GET /api/fleets/        - List user's fleets
    create:   POST /api/fleets/       - Create a fleet (owner = current user)
    retrieve: GET /api/fleets/{id}/   - Fleet detail (only if owner)
    """
    
    serializer_class = FleetSerializer
    
    def get_queryset(self):
        """Return only fleets owned by the authenticated user."""
        return Fleet.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically set the owner to the current user."""
        serializer.save(owner=self.request.user)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing devices.
    
    Users can only see and manage devices in fleets they own.
    
    list:     GET /api/devices/        - List devices in user's fleets
    create:   POST /api/devices/       - Create device in owned fleet
    retrieve: GET /api/devices/{id}/   - Device detail (only if in owned fleet)
    update:   PUT /api/devices/{id}/   - Update device (only if in owned fleet)
    partial:  PATCH /api/devices/{id}/ - Partial update (only if in owned fleet)
    destroy:  DELETE /api/devices/{id}/- Delete device (only if in owned fleet)
    """
    
    serializer_class = DeviceSerializer
    
    def get_queryset(self):
        """Return only devices in fleets owned by the authenticated user."""
        return Device.objects.filter(fleet__owner=self.request.user)
