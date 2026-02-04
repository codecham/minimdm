import pytest

from mdm.models import Device, Fleet


@pytest.mark.django_db
class TestDeviceList:
    """Tests for GET /api/devices/"""

    endpoint = '/api/devices/'

    def test_user_sees_only_own_devices(self, auth_client, device, other_device):
        """Users only see devices in their own fleets."""
        response = auth_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == device.id

    def test_filter_devices_by_fleet(self, auth_client, user, device):
        """Users can filter devices by fleet."""
        fleet2 = Fleet.objects.create(name='Fleet 2', owner=user)
        device2 = Device.objects.create(fleet=fleet2, os_version=14)

        response = auth_client.get(f'{self.endpoint}?fleet={fleet2.id}')

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == device2.id

    def test_filter_by_other_users_fleet_returns_empty(self, auth_client, other_fleet):
        """Filtering by another user's fleet returns empty list."""
        response = auth_client.get(f'{self.endpoint}?fleet={other_fleet.id}')

        assert response.status_code == 200
        assert len(response.data) == 0


@pytest.mark.django_db
class TestDeviceCreate:
    """Tests for POST /api/devices/"""

    endpoint = '/api/devices/'

    def test_user_can_create_device_in_own_fleet(self, auth_client, fleet):
        """Users can create devices in their own fleets."""
        response = auth_client.post(self.endpoint, {
            'fleet': fleet.id,
            'os_version': 15,
        })

        assert response.status_code == 201
        assert response.data['fleet'] == fleet.id
        assert response.data['os_version'] == 15
        assert 'serial_number' in response.data

    def test_user_cannot_create_device_in_other_fleet(self, auth_client, other_fleet):
        """Users cannot create devices in fleets they don't own."""
        response = auth_client.post(self.endpoint, {
            'fleet': other_fleet.id,
            'os_version': 15,
        })

        assert response.status_code == 400
        assert 'fleet' in response.data

    def test_device_without_os_version(self, auth_client, fleet):
        """Devices can be created without os_version."""
        response = auth_client.post(self.endpoint, {
            'fleet': fleet.id,
        })

        assert response.status_code == 201
        assert response.data['os_version'] is None


@pytest.mark.django_db
class TestDeviceDetail:
    """Tests for GET /api/devices/{id}/"""

    def test_user_can_view_own_device(self, auth_client, device):
        """Users can view devices in their own fleets."""
        response = auth_client.get(f'/api/devices/{device.id}/')

        assert response.status_code == 200
        assert response.data['id'] == device.id

    def test_user_cannot_view_other_device(self, auth_client, other_device):
        """Users cannot view devices in other users' fleets."""
        response = auth_client.get(f'/api/devices/{other_device.id}/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestDeviceUpdate:
    """Tests for PUT/PATCH /api/devices/{id}/"""

    def test_user_can_update_own_device(self, auth_client, device):
        """Users can update devices in their own fleets."""
        response = auth_client.patch(f'/api/devices/{device.id}/', {
            'os_version': 99,
        })

        assert response.status_code == 200
        assert response.data['os_version'] == 99

    def test_user_cannot_update_other_device(self, auth_client, other_device):
        """Users cannot update devices in other users' fleets."""
        response = auth_client.patch(f'/api/devices/{other_device.id}/', {
            'os_version': 99,
        })

        assert response.status_code == 404

    def test_user_can_move_device_to_own_fleet(self, auth_client, user, device):
        """Users can move devices between their own fleets."""
        new_fleet = Fleet.objects.create(name='New Fleet', owner=user)

        response = auth_client.patch(f'/api/devices/{device.id}/', {
            'fleet': new_fleet.id,
        })

        assert response.status_code == 200
        assert response.data['fleet'] == new_fleet.id

    def test_user_cannot_move_device_to_other_fleet(self, auth_client, device, other_fleet):
        """Users cannot move devices to fleets they don't own."""
        response = auth_client.patch(f'/api/devices/{device.id}/', {
            'fleet': other_fleet.id,
        })

        assert response.status_code == 400


@pytest.mark.django_db
class TestDeviceDelete:
    """Tests for DELETE /api/devices/{id}/"""

    def test_user_can_delete_own_device(self, auth_client, device):
        """Users can delete devices in their own fleets."""
        response = auth_client.delete(f'/api/devices/{device.id}/')

        assert response.status_code == 204
        assert not Device.objects.filter(id=device.id).exists()

    def test_user_cannot_delete_other_device(self, auth_client, other_device):
        """Users cannot delete devices in other users' fleets."""
        response = auth_client.delete(f'/api/devices/{other_device.id}/')

        assert response.status_code == 404
        assert Device.objects.filter(id=other_device.id).exists()