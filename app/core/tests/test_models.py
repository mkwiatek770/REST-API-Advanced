from django.test import TestCase
from django.contrib.auth import get_user_model


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
