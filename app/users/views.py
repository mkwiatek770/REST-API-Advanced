from rest_framework import generics
from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user view."""

    serializer_class = UserSerializer
