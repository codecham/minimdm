import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthentication:
    """Tests for authentication endpoints."""

    endpoint = '/api/auth/token/'

    def test_obtain_token_with_valid_credentials(self, api_client):
        """Users can obtain a token with valid credentials."""
        User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

        response = api_client.post(self.endpoint, {
            'username': 'testuser',
            'password': 'testpass123',
        })

        assert response.status_code == 200
        assert 'token' in response.data

    def test_obtain_token_with_invalid_password(self, api_client, user):
        """Token request fails with wrong password."""
        response = api_client.post(self.endpoint, {
            'username': 'alice',
            'password': 'wrongpassword',
        })

        assert response.status_code == 400

    def test_obtain_token_with_invalid_username(self, api_client):
        """Token request fails with non-existent user."""
        response = api_client.post(self.endpoint, {
            'username': 'nonexistent',
            'password': 'password123',
        })

        assert response.status_code == 400

    def test_protected_endpoint_without_token(self, api_client):
        """Protected endpoints reject unauthenticated requests."""
        response = api_client.get('/api/fleets/')

        assert response.status_code == 401
    
    def test_token_response_includes_user_info(self, api_client):
        """Token response includes user_id and username."""
        User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

        response = api_client.post(self.endpoint, {
            'username': 'testuser',
            'password': 'testpass123',
        })

        assert response.status_code == 200
        assert 'token' in response.data
        assert 'user_id' in response.data
        assert 'username' in response.data
        assert response.data['username'] == 'testuser'