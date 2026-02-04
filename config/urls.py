from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from drf_spectacular.utils import extend_schema

class TokenRequestSerializer(serializers.Serializer):
    """Serializer for token request documentation."""
    username = serializers.CharField(help_text="Your username")
    password = serializers.CharField(help_text="Your password")


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response documentation."""
    token = serializers.CharField(help_text="Authentication token")


@extend_schema(tags=['Authentication'])
class DocumentedObtainAuthToken(ObtainAuthToken):
    """Custom ObtainAuthToken with Swagger documentation."""
    
    @extend_schema(
        summary="Obtain authentication token",
        description="Exchange username and password for an authentication token.",
        request=TokenRequestSerializer,
        responses={200: TokenResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
        })

urlpatterns = [
    path('admin/', admin.site.urls),
	path('api/auth/token/', DocumentedObtainAuthToken.as_view(), name='api_token_auth'),
	path('api/', include('mdm.urls')),
	path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
