from django.contrib.auth.models import User
from rest_framework	import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Fleet, Device
from .serializers import FleetSerializer, UserSerializer, DeviceSerializer
from .permissions import IsAdminUser, IsAdminOrSelf, permissions


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    User management endpoints.
    
    **Permissions:** Admin only, except users can view their own profile.
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
        elif self.action == 'me':
            return [permissions.IsAuthenticated()]
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
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Return the authenticated user's profile.
        
        GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    
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
