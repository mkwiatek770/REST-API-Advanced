from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_tags(self):
        """Test retrieving tags."""
        tag1 = Tag.objects.create(name='Soy', user=self.user)
        tag2 = Tag.objects.create(name='Vegan', user=self.user)
        expected_tags = TagSerializer(Tag.objects.all().order_by('-name'), many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_tags.data)

    def test_tags_limited_to_user(self):
        """Test retrieving only user's tags."""
        tag1 = Tag.objects.create(name='Soy', user=self.user)
        other_user = get_user_model().objects.create_user('test@gmail.com', 'password123')
        tag2 = Tag.objects.create(name='Vegan', user=other_user)
        expected_tags = TagSerializer(Tag.objects.filter(user=self.user), many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_tags.data)