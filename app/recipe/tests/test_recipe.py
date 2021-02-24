import tempfile
import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def get_recipe_detail_url(pk: int):
    return reverse('recipe:recipe-detail', args=[pk])


def get_image_upload_url(pk: int):
    return reverse('recipe:recipe-upload-image', args=[pk])


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
            Recipe.objects.all().order_by('-id'), many=True
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

    def test_recipe_detail(self):
        """Test retrieving recipe detail data."""
        recipe = Recipe.objects.create(
            title='Recipe 1', user=self.user, time_minutes=6, price=4.00
        )
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        ingredient = Ingredient.objects.create(user=self.user, name='Ingredient 1')
        recipe.tags.add(tag)
        recipe.ingredients.add(ingredient)
        serializer = RecipeDetailSerializer(recipe)

        url = get_recipe_detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data['tags'][0]['name'], tag.name)
        self.assertEqual(res.data['ingredients'][0]['name'], ingredient.name)

    def test_recipe_detail_of_other_user(self):
        """Make user user can retrieve his own recipe detail views."""
        other_user = get_user_model().objects.create_user(
            'other@gmail.com', 'password123'
        )
        recipe = Recipe.objects.create(
            title='Recipe 1', user=other_user, time_minutes=6, price=4.00
        )

        url = get_recipe_detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_recipe_create_success(self):
        """Test creating a new recipe."""
        payload = {'title': 'New Recipe', 'time_minutes': 5, 'price': 3.33}

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Recipe.objects.filter(title=payload['title']).exists())

    def test_recipe_with_tags_create_success(self):
        """Test creating a new recipe with tags."""
        tag_1 = Tag.objects.create(user=self.user, name='tag 1')
        tag_2 = Tag.objects.create(user=self.user, name='tag 2')
        payload = {
            'title': 'New Recipe',
            'time_minutes': 5,
            'price': 3.33,
            'tags': [tag_1.id, tag_2.id],
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title=payload['title'])
        tags = recipe.tags.all()
        self.assertIn(tag_1, tags)
        self.assertIn(tag_2, tags)

    def test_recipe_with_ingredients_create_success(self):
        """Test creating a new recipe with ingredients."""
        ingredient_1 = Ingredient.objects.create(user=self.user, name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(user=self.user, name='Ingredient 2')
        payload = {
            'title': 'New Recipe',
            'time_minutes': 5,
            'price': 3.33,
            'ingredients': [ingredient_1.id, ingredient_2.id],
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(title=payload['title'])
        ingredients = recipe.ingredients.all()
        self.assertIn(ingredient_1, ingredients)
        self.assertIn(ingredient_2, ingredients)

    def test_partial_update_recipe(self):
        """Test HTTP PATCH is possible on existing recipe objects."""
        recipe = Recipe.objects.create(
            user=self.user, title='Chickenn', time_minutes=5, price=10.00
        )
        tag = Tag.objects.create(user=self.user, name='Tag')
        payload = {
            'title': 'Chicken with vegetables',
            'tags': [tag.id],
        }

        url = get_recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag, recipe.tags.all())
        self.assertEqual(recipe.title, payload['title'])

    def test_full_update_recipe(self):
        """Test HTTP PUT is possible on existing recipe objects."""
        recipe = Recipe.objects.create(
            user=self.user, title='Chickenn', time_minutes=5, price=10.00
        )
        tag = Tag.objects.create(user=self.user, name='Tag')
        recipe.tags.add(tag)
        payload = {
            'title': 'Chicken with vegetables',
            'time_minutes': 1,
            'price': 69.00,
        }

        url = get_recipe_detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag, recipe.tags.all())
        self.assertEqual(recipe.title, payload['title'])


class RecipeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass',
        )
        self.client.force_authenticate(self.user)
        self.recipe = Recipe.objects.create(
            user=self.user, title='Sample', time_minutes=1, price=1.0
        )

    def test_upload_image_to_recipe(self):
        """test uploading image to recipe."""
        url = get_image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = get_image_upload_url(self.recipe.id)

        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.recipe.image)

    def tearDown(self):
        self.recipe.image.delete()
