from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FleetViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('fleets', FleetViewSet, basename='fleet')

urlpatterns = [
    path('', include(router.urls)),
]