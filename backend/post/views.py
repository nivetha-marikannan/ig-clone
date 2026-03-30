from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Post, Comment, Like
from .serializers import PostSerializer
from user.models import User

class PostCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                'success': True,
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        })
    
class PostDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_post(self, pk, request):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None
    
    def get(self, request, pk):
        post = self.get_post(pk, request)
        if not post:
            return Response({
                'success': False,
                'error': 'Post not found'
            })
        serializer = PostSerializer(post)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def patch(self, request, pk):
        post = self.get_post(pk, request)
        if not post:
            return Response({
                'success': False,
                'error': 'Post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({
                'success': False,
                'error': 'You can only update your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_post(pk, request)
        if not post:
            return Response({
                'success': False,
                'error': 'Post not found'
            }, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({
                'success': False,
                'error': 'You can only delete your own posts'
            }, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({
            'success': True,
            'message': 'Post deleted successfully'
        }, status=status.HTTP_200_OK)