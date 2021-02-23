from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


class PublicRecipesApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving recipes."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123',
        )
        self.client.force_authenticate(self.user)

    def _create_recipe(self, **params):
        return Recipe.objects.create(**params)

    def test_retrieve_recipes(self):
        """Test retrieving recipes."""
        recipe_1 = self._create_recipe(
            title='Recipe 1', user=self.user, time_minutes=5, price=10.00
        )
        recipe_1.ingredients.add(
            Ingredient.objects.create(name='cucumber', user=self.user),
            Ingredient.objects.create(name='tomato', user=self.user),
        )
        recipe_1.tags.add(
            Tag.objects.create(name='tag1', user=self.user),
            Tag.objects.create(name='tag2', user=self.user),
        )
        self._create_recipe(
            title='Recipe 2', user=self.user, time_minutes=3, price=12.50
        )
        expected_recipes = RecipeSerializer(
            Recipe.objects.all().order_by('-title'), many=True
        )

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_recipes.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving only user's tags."""
        self._create_recipe(
            title='Recipe 1', user=self.user, time_minutes=6, price=4.00
        )
        other_user = get_user_model().objects.create_user(
            'other@gmail.com', 'password123'
        )
        self._create_recipe(
            title='Recipe 2', user=other_user, time_minutes=1, price=4.00
        )
        expected_recipes = RecipeSerializer(
            Recipe.objects.filter(user=self.user), many=True
        )

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_recipes.data)
