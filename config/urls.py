from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from mdm.authentication import DocumentedObtainAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', DocumentedObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/', include('mdm.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]