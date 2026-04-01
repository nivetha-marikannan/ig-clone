from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from user.models import User

class PostCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors})
    
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
            return Response({'success': False, 'error': 'Post not found'})
        serializer = PostSerializer(post)
        return Response({'success': True, 'data': serializer.data})
    
    def patch(self, request, pk):
        post = self.get_post(pk, request)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({'success': False, 'error': 'You can only update your own posts'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_post(pk, request)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({'success': False, 'error': 'You can only delete your own posts'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({'success': True, 'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)


class CommentListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None

    def get(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({'success': True, 'data': serializer.data})

    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_comment(self, post_id, comment_id):
        try:
            return Comment.objects.get(id=comment_id, post_id=post_id)
        except Comment.DoesNotExist:
            return None

    def get(self, request, post_id, comment_id):
        comment = self.get_comment(post_id, comment_id)
        if not comment:
            return Response({'success': False, 'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentSerializer(comment)
        return Response({'success': True, 'data': serializer.data})

    def patch(self, request, post_id, comment_id):
        comment = self.get_comment(post_id, comment_id)
        if not comment:
            return Response({'success': False, 'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.user != request.user:
            return Response({'success': False, 'error': 'You can only update your own comments'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        comment = self.get_comment(post_id, comment_id)
        if not comment:
            return Response({'success': False, 'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.user != request.user:
            return Response({'success': False, 'error': 'You can only delete your own comments'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response({'success': True, 'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)


class LikeListCreateView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None

    def get(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        likes = Like.objects.filter(post=post).order_by('-created_at')
        serializer = LikeSerializer(likes, many=True)
        return Response({'success': True, 'likes_count': likes.count(), 'data': serializer.data})

    def post(self, request, post_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        existing_like = Like.objects.filter(user=request.user, post=post).first()
        
        if existing_like:
            existing_like.delete()
            return Response({'success': True, 'message': 'Post unliked', 'liked': False}, status=status.HTTP_200_OK)
        else:
            try:
                like = Like.objects.create(user=request.user, post=post)
                serializer = LikeSerializer(like)
                return Response({'success': True, 'message': 'Post liked', 'liked': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LikeDetailView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None

    def get_like(self, post_id, like_id):
        try:
            return Like.objects.get(id=like_id, post_id=post_id)
        except Like.DoesNotExist:
            return None

    def get(self, request, post_id, like_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        like = self.get_like(post_id, like_id)
        if not like:
            return Response({'success': False, 'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LikeSerializer(like)
        return Response({'success': True, 'data': serializer.data})

    def delete(self, request, post_id, like_id):
        post = self.get_post(post_id)
        if not post:
            return Response({'success': False, 'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        like = self.get_like(post_id, like_id)
        if not like:
            return Response({'success': False, 'error': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if like.user != request.user:
            return Response({'success': False, 'error': 'You can only delete your own likes'}, status=status.HTTP_403_FORBIDDEN)
        
        like.delete()
        return Response({'success': True, 'message': 'Like deleted successfully'}, status=status.HTTP_200_OK)