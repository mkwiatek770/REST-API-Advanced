from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_sample_user(email='test@gmail.com', password='testpass', **params):
    return get_user_model().objects.create_user(email, password, **params)


class ModelTest(TestCase):
    def test_create_user_with_email_successfull(self):
        """Test creating user with email is successful."""
        email = 'some@gmail.com'
        password = 'Testpass1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):
        """Test input email is case insensitive."""
        email = "some@GMAIL.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password='Testpass1234',
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no emial raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'pass123')

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
            email='some@gmail.com',
            password='password123',
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(
            user=create_sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test Ingredient str representation."""
        ingredient = models.Ingredient.objects.create(
            user=create_sample_user(),
            name='Tomato',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test recipe string representation."""
        recipe = models.Recipe.objects.create(
            user=create_sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00,
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_under_uuid(self, mock_uuid):
        """Test that image is saved in the correct location."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        expected_path = f'uploads/recipe/{uuid}.jpg'

        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        
        self.assertEqual(file_path, expected_path)
