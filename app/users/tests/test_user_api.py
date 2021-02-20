from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users API (public)."""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful."""
        payload = {
            'email': 'someuser@gmail.com',
            'password1': 'testpass',
            'password2': 'testpass',
            'name': 'Joe Doe',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', res.data)
        self.assertTrue(get_user_model().objects.filter(**res.data).exists())

    def test_user_exists(self):
        """Test creating user that already exists fails."""
        payload = {
            'email': 'some@gmail.com',
            'password1': 'test1234',
            'password2': 'test1234',
        }
        create_user(email=payload['email'], password=payload['password1'])

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test that password must be more than 5 characters."""
        payload = {'email': 'some@gmail.com', 'password1': '1234', 'password2': '1234'}

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            get_user_model().objects.filter(email=payload['email']).exists()
        )

    def test_passwords_dont_match(self):
        """Test user is not created if password dont match."""
        payload = {
            'email': 'some@gmail.com',
            'password1': 'test1234',
            'password2': 'otherpass',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            get_user_model().objects.filter(email=payload['email']).exists()
        )

    def test_create_token_for_user(self):
        """Test that token is in returted payload after authtentication."""
        payload = {'email': 'test@gmail.com', 'password': 'pass123'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_token_invalid_credentials(self):
        """Test token is not created for invalid credentials,"""
        create_user(email='some@gmail.com', password='password123')
        payload = {'email': 'some@gmail.com', 'password': 'wrongpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_no_user(self):
        payload = {'email': 'notexisting@gmail.com', 'password': '12345'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
