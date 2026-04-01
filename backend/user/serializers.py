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

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'is_private', 'dob', 'created_at']
        read_only_fields = ['id', 'created_at']


class FollowUserSerializer(serializers.Serializer):
    
    def validate(self, data):
        
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        user_id = self.context.get('user_id')
        
        if not user_id:
            raise serializers.ValidationError("User ID required")
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user not found")
        
        if request.user.id == target_user.id:
            raise serializers.ValidationError("Cannot follow yourself")
        
        return data


class FollowersListSerializer(serializers.ModelSerializer):
    
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_following']
    
    def get_is_following(self, obj):
        
        from .models import Follow
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            return False
        
        return Follow.objects.filter(
            follower=request.user,
            following=obj
        ).exists()
