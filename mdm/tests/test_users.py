import pytest


@pytest.mark.django_db
class TestUserList:
    """Tests for GET /api/users/"""

    endpoint = '/api/users/'

    def test_admin_can_list_users(self, admin_client, user):
        """Admin can see all users."""
        response = admin_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_regular_user_cannot_list_users(self, auth_client):
        """Regular users cannot list all users."""
        response = auth_client.get(self.endpoint)

        assert response.status_code == 403

    def test_unauthenticated_cannot_list_users(self, api_client):
        """Unauthenticated requests are rejected."""
        response = api_client.get(self.endpoint)

        assert response.status_code == 401


@pytest.mark.django_db
class TestUserCreate:
    """Tests for POST /api/users/"""

    endpoint = '/api/users/'

    def test_admin_can_create_user(self, admin_client):
        """Admin can create new users."""
        response = admin_client.post(self.endpoint, {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
        })

        assert response.status_code == 201
        assert response.data['username'] == 'newuser'
        assert 'password' not in response.data  # Password should not be returned

    def test_regular_user_cannot_create_user(self, auth_client):
        """Regular users cannot create new users."""
        response = auth_client.post(self.endpoint, {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
        })

        assert response.status_code == 403

    def test_create_user_with_short_password(self, admin_client):
        """User creation fails with password < 8 characters."""
        response = admin_client.post(self.endpoint, {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'short',
        })

        assert response.status_code == 400


@pytest.mark.django_db
class TestUserDetail:
    """Tests for GET /api/users/{id}/"""

    def test_admin_can_view_any_user(self, admin_client, user):
        """Admin can view any user's profile."""
        response = admin_client.get(f'/api/users/{user.id}/')

        assert response.status_code == 200
        assert response.data['username'] == 'alice'

    def test_user_can_view_own_profile(self, auth_client, user):
        """Users can view their own profile."""
        response = auth_client.get(f'/api/users/{user.id}/')

        assert response.status_code == 200
        assert response.data['username'] == 'alice'

    def test_user_cannot_view_other_profile(self, auth_client, other_user):
        """Users cannot view other users' profiles."""
        response = auth_client.get(f'/api/users/{other_user.id}/')

        assert response.status_code == 403

    def test_user_profile_includes_fleets(self, auth_client, user, fleet):
        """User profile includes their fleets."""
        response = auth_client.get(f'/api/users/{user.id}/')

        assert response.status_code == 200
        assert 'fleets' in response.data
        assert len(response.data['fleets']) == 1
        assert response.data['fleets'][0]['name'] == 'Alice Fleet'


@pytest.mark.django_db
class TestUserMe:
    """Tests for GET /api/users/me/"""

    endpoint = '/api/users/me/'

    def test_authenticated_user_can_access_own_profile(self, auth_client, user):
        """Authenticated users can access their own profile via /me/."""
        response = auth_client.get(self.endpoint)

        assert response.status_code == 200
        assert response.data['username'] == 'alice'

    def test_me_includes_fleets(self, auth_client, user, fleet):
        """The /me/ endpoint includes the user's fleets."""
        response = auth_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.data['fleets']) == 1

    def test_unauthenticated_cannot_access_me(self, api_client):
        """Unauthenticated requests are rejected."""
        response = api_client.get(self.endpoint)

        assert response.status_code == 401