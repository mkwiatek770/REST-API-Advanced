from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from users.serializers import UserSerializer, AuthUserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user view."""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthUserSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
