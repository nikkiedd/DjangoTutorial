from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email='a@a.com', password='passworddd'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'email@address.com'
        password = 'pass'
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_new_user_email_normalized(self):
        """Test that the email for a new user is normalized"""
        email = 'email@GMAIL.com'
        user = get_user_model().objects.create_user(email=email, password='abc')

        self.assertEqual(user.email, email.lower())
    
    def test_new_user_invalid_email(self):
        """Test that creating a user without an email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'val')
    
    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser('email@email.com', 'pass')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)