from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FleetViewSet, DeviceViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('fleets', FleetViewSet, basename='fleet')
router.register('devices', DeviceViewSet, basename='device')


urlpatterns = [
    path('', include(router.urls)),
]