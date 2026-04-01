from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, User, Follow
from .serializers import ProfileSerializer, RegisterSerializer, FollowUserSerializer, FollowersListSerializer

class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({'success': True, 'access': str(refresh.access_token), 'refresh': str(refresh), 'user': {'id': user.id, 'email': user.email, 'username': user.username}}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            profile = Profile.objects.select_related('user').get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({'success': False, 'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile)
        return Response({'success': True, 'data': serializer.data})


class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.select_related('user').get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'success': False, 'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile)
        return Response({'success': True, 'data': serializer.data})

    def patch(self, request):
        try:
            profile = Profile.objects.select_related('user').get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'success': False, 'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FollowToggleView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        serializer = FollowUserSerializer(data={}, context={'request': request, 'user_id': user_id})
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        follow_record = Follow.objects.filter(follower=request.user, following=target_user).first()
        if follow_record:
            follow_record.delete()
            following = False
            message = "Unfollowed user"
        else:
            Follow.objects.create(follower=request.user, following=target_user)
            following = True
            message = "Now following user"
        return Response({'success': True, 'message': message, 'following': following, 'followers_count': target_user.followers.count()}, status=status.HTTP_200_OK)


class FollowersListView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        followers = user.followers.all()
        serializer = FollowersListSerializer(followers, many=True, context={'request': request})
        return Response({'success': True, 'followers_count': followers.count(), 'data': serializer.data}, status=status.HTTP_200_OK)


class FollowingListView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        following = user.following.all()
        serializer = FollowersListSerializer(following, many=True, context={'request': request})
        return Response({'success': True, 'following_count': following.count(), 'data': serializer.data}, status=status.HTTP_200_OK)


class FollowStatusView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
        return Response({'success': True, 'is_following': is_following, 'target_user': {'id': target_user.id, 'username': target_user.username}}, status=status.HTTP_200_OK)
