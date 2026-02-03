from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from .serializers import UserSerializer
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