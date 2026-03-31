from rest_framework import serializers
from .models import Post, Comment, Like
from user.models import User

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'image', 'caption', 'hashtags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'image', 'created_at', 'updated_at', 'hashtags']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'user', 'created_at', 'updated_at']
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'post', 'user', 'created_at']