from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import Profile, User


class RegisterSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        return value
    
    def create(self, validated_data):
        with transaction.atomic():
            hashed_password = make_password(validated_data['password'])
            
            user = User.objects.create(
                email=validated_data['email'],
                username=validated_data['username'],
                password=hashed_password
            )
            
            Profile.objects.create(user=user)
            
            return user

class LogoutSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        try:
            RefreshToken(value)
        except (InvalidToken, TokenError):
            raise serializers.ValidationError("Invalid refresh token.")
        
        return value
    
    def save(self):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
        
        refresh_token = self.validated_data['refresh']
        token = RefreshToken(refresh_token)
        
        token.blacklist()
        
        return {"message": "Successfully logged out"}


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'is_private', 'dob', 'created_at']
        read_only_fields = ['id', 'created_at']
