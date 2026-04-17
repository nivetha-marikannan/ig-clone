from rest_framework import serializers
from .models import Post, Comment, Like
from user.models import User

class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'image', 'caption', 'hashtags', 'likes_count', 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'image', 'created_at', 'updated_at', 'hashtags']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'post', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'user', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username
        }
    
class LikeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'post', 'user', 'created_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username
        }