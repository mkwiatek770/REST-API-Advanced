from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.authentication import authenticate


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object."""

    password1 = serializers.CharField(write_only=True, min_length=5)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2', 'name')
        # extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        if password1 != password2:
            raise serializers.ValidationError('Passwords do not match.')
        data['password'] = password1
        del data['password1']
        del data['password2']
        return data

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)


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
