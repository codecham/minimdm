import pytest

from mdm.models import Fleet


@pytest.mark.django_db
class TestFleetList:
    """Tests for GET /api/fleets/"""

    endpoint = '/api/fleets/'

    def test_user_sees_only_own_fleets(self, auth_client, fleet, other_fleet):
        """Users only see fleets they own."""
        response = auth_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Alice Fleet'

    def test_unauthenticated_cannot_list_fleets(self, api_client):
        """Unauthenticated requests are rejected."""
        response = api_client.get(self.endpoint)

        assert response.status_code == 401


@pytest.mark.django_db
class TestFleetCreate:
    """Tests for POST /api/fleets/"""

    endpoint = '/api/fleets/'

    def test_user_can_create_fleet(self, auth_client, user):
        """Users can create fleets."""
        response = auth_client.post(self.endpoint, {
            'name': 'New Fleet',
        })

        assert response.status_code == 201
        assert response.data['name'] == 'New Fleet'
        assert response.data['owner'] == user.id

    def test_fleet_owner_is_auto_assigned(self, auth_client, user):
        """Fleet owner is automatically set to current user."""
        response = auth_client.post(self.endpoint, {
            'name': 'Auto Owner Fleet',
        })

        fleet = Fleet.objects.get(id=response.data['id'])
        assert fleet.owner == user

    def test_cannot_create_duplicate_fleet_name(self, auth_client, fleet):
        """Users cannot create two fleets with the same name."""
        response = auth_client.post(self.endpoint, {
            'name': 'Alice Fleet',
        })

        assert response.status_code == 400


@pytest.mark.django_db
class TestFleetDetail:
    """Tests for GET /api/fleets/{id}/"""

    def test_user_can_view_own_fleet(self, auth_client, fleet):
        """Users can view their own fleet details."""
        response = auth_client.get(f'/api/fleets/{fleet.id}/')

        assert response.status_code == 200
        assert response.data['name'] == 'Alice Fleet'

    def test_user_cannot_view_other_fleet(self, auth_client, other_fleet):
        """Users cannot view fleets they don't own (returns 404)."""
        response = auth_client.get(f'/api/fleets/{other_fleet.id}/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestFleetDeviceCount:
    """Tests for device_count in fleet responses."""

    endpoint = '/api/fleets/'

    def test_fleet_includes_device_count(self, auth_client, fleet, device):
        """Fleet response includes the number of devices."""
        response = auth_client.get(f'{self.endpoint}{fleet.id}/')

        assert response.status_code == 200
        assert response.data['device_count'] == 1

    def test_fleet_device_count_is_zero(self, auth_client, fleet):
        """Empty fleet has device_count of 0."""
        response = auth_client.get(f'{self.endpoint}{fleet.id}/')

        assert response.status_code == 200
        assert response.data['device_count'] == 0