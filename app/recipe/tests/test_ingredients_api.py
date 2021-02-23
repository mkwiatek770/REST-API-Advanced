from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Make sure only authenticated user has access."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@email.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients."""
        Ingredient.objects.create(name='Tomato', user=self.user)
        Ingredient.objects.create(name='Cucumber', user=self.user)
        expected_ingredients = IngredientSerializer(
            Ingredient.objects.all().order_by('-name'), many=True
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_ingredients.data)

    def test_ingredients_limited_to_user(self):
        """Test retrieving only user's ingredients."""
        Ingredient.objects.create(name='Potato', user=self.user)
        other_user = get_user_model().objects.create_user(
            'other@gmail.com', 'password123'
        )
        Ingredient.objects.create(name='Salad', user=other_user)
        expected_ingredients = IngredientSerializer(
            Ingredient.objects.filter(user=self.user), many=True
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_ingredients.data)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient."""
        payload = {'name': 'New Ingredient'}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(name=payload['name']).exists())

    def test_create_ingredient_invalid(self):
        """Test creating a ingredient with an invalid payload."""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Ingredient.objects.count(), 0)
