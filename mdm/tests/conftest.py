import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from mdm.models import Fleet, Device


# =============================================================================
# API CLIENT
# =============================================================================

@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    """Return an API client authenticated as regular user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin):
    """Return an API client authenticated as admin."""
    api_client.force_authenticate(user=admin)
    return api_client


# =============================================================================
# USERS
# =============================================================================

@pytest.fixture
def admin(db):
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def user(db):
    """Create a regular user."""
    return User.objects.create_user(
        username='alice',
        email='alice@test.com',
        password='alice123',
    )


@pytest.fixture
def other_user(db):
    """Create another regular user."""
    return User.objects.create_user(
        username='bob',
        email='bob@test.com',
        password='bob123',
    )


# =============================================================================
# FLEETS
# =============================================================================

@pytest.fixture
def fleet(db, user):
    """Create a fleet owned by user."""
    return Fleet.objects.create(
        name='Alice Fleet',
        owner=user,
    )


@pytest.fixture
def other_fleet(db, other_user):
    """Create a fleet owned by other_user."""
    return Fleet.objects.create(
        name='Bob Fleet',
        owner=other_user,
    )


# =============================================================================
# DEVICES
# =============================================================================

@pytest.fixture
def device(db, fleet):
    """Create a device in user's fleet."""
    return Device.objects.create(
        fleet=fleet,
        os_version=12,
    )


@pytest.fixture
def other_device(db, other_fleet):
    """Create a device in other_user's fleet."""
    return Device.objects.create(
        fleet=other_fleet,
        os_version=10,
    )