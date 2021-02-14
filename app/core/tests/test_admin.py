from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='password123',
        )
        self.user = get_user_model().objects.create_user(
            email='client@gmail.com',
            password='password123',
            name='Full Name'
        )
        self.client.force_login(self.admin_user)

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
