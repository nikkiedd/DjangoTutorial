from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""
    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the authorized user ingredients API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'mail@mail.com',
            'password123'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Spinach')
        Ingredient.objects.create(user=self.user, name='Curry')

        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_ingredients_limited_to_user(self):
        """Test that only the ingredients for the authorized use rhave been retrieved"""
        user2 = get_user_model().objects.create_user(
            'othermail@whatevs.com',
            'kewllllll'
        )

        Ingredient.objects.create(user=user2, name='cheese')
        ingredient = Ingredient.objects.create(user=self.user, name='chocolate')

        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
    
    def test_ingredients_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'Meat'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)


    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name':''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering only ingredients assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Apple'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple pie',
            time_minutes=20,
            price=16.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)