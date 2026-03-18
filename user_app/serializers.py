import re

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=3,
        max_length=150,
    )
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        min_length=8,
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2"]

    def validate_username(self, value):
        sanitized = value.strip().lower()
        if not re.match(r"^[\w.@+-]+$", sanitized):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and @/./+/-/_"
            )
        if User.objects.filter(username=sanitized).exists():
            raise serializers.ValidationError("Username already exists")
        return sanitized

    def validate_email(self, value):
        sanitized = value.strip().lower()
        if User.objects.filter(email=sanitized).exists():
            raise serializers.ValidationError("Email already registered")
        return sanitized

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data["username"] = validated_data["username"].lower()
        validated_data["email"] = validated_data["email"].lower()

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = ["id"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(
        required=False,
        write_only=True,
    )

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token

    def validate(self, attrs):
        username = attrs.get("username", "")
        if username:
            attrs["username"] = username.lower()

        data = super().validate(attrs)
        user_serializer = UserSerializer(self.user).data
        data["user"] = user_serializer
        return data
