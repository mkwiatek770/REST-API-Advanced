from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag object(s)."""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredient object(s)."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe object(s)."""

    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link', 'ingredients', 'tags')
        read_only_fields = ('id', 'ingredients', 'tags')
