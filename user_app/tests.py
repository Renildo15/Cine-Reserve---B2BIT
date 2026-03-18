from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user_app.serializers import (
    MyTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterSerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password2": "DifferentPass123!",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_missing_required_fields(self):
        data = {"username": "testuser"}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertIn("password2", serializer.errors)

    def test_create_user(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))


class UserSerializerTest(TestCase):
    def test_contains_expected_fields(self):
        user = User.objects.create_user(username="testuser", email="test@example.com", password="pass123")
        serializer = UserSerializer(user)
        self.assertEqual(set(serializer.data.keys()), {"id", "username", "email"})

    def test_email_is_optional(self):
        user = User.objects.create_user(username="testuser", password="pass123")
        serializer = UserSerializer(user)
        self.assertIn("email", serializer.data)


class MyTokenObtainPairSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_serializer_has_get_token_method(self):
        serializer = MyTokenObtainPairSerializer()
        self.assertTrue(hasattr(serializer, "get_token"))


class UserRegisterViewTest(APITestCase):
    def test_register_user_success(self):
        url = reverse("users:user_register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch(self):
        url = reverse("users:user_register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "DifferentPass123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        User.objects.create_user(username="existinguser", password="pass123")
        url = reverse("users:user_register")
        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        url = reverse("users:user_register")
        data = {"username": "newuser"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_login_success(self):
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_login_wrong_password(self):
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        url = reverse("token_obtain_pair")
        data = {"username": "nonexistent", "password": "pass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_response_contains_user_data(self):
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.data["user"]["username"], "testuser")
