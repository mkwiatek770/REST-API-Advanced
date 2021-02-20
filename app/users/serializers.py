from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.authentication import authenticate


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user object."""

    password1 = serializers.CharField(write_only=True, min_length=5)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2', 'name')
        # extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def validate(self, data):
        password1 = data.pop('password1')
        password2 = data.pop('password2')
        if password1 != password2:
            raise serializers.ValidationError('Passwords do not match.')
        data['password'] = password1
        return data

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for modifying user object."""

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def update(self, instance, validated_data):
        """Update a user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthUserSerializer(serializers.Serializer):
    """Serializer for the user authentication object."""

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, data):
        """Validate and authenticate the user."""
        email = data.get('email')
        password = data.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authentication')
        data['user'] = user
        return data
