from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
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
        Tag.objects.create(name='Soy', user=self.user)
        Tag.objects.create(name='Vegan', user=self.user)
        expected_tags = TagSerializer(Tag.objects.all().order_by('-name'), many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_tags.data)

    def test_tags_limited_to_user(self):
        """Test retrieving only user's tags."""
        Tag.objects.create(name='Soy', user=self.user)
        other_user = get_user_model().objects.create_user(
            'other@gmail.com', 'password123'
        )
        Tag.objects.create(name='Vegan', user=other_user)
        expected_tags = TagSerializer(Tag.objects.filter(user=self.user), many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_tags.data)

    def test_create_tag_successful(self):
        """Test creating a new tag."""
        payload = {'name': 'New Tag'}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name=payload['name']).exists())

    def test_create_tag_invalid(self):
        """Test creating a tag with an invalid payload."""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Tag.objects.count(), 0)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test retrieving only those tags that are assigned by recipe."""
        tag_1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag_2 = Tag.objects.create(user=self.user, name='Tag 2')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Some title',
            price=10.0,
            time_minutes=1,
        )
        recipe.tags.add(tag_1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertIn(TagSerializer(tag_1).data, res.data)
        self.assertNotIn(TagSerializer(tag_2).data, res.data)
