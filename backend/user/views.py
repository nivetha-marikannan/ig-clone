from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from .serializers import ProfileSerializer, RegisterSerializer, LogoutSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        serializer = LogoutSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response(
                {
                    'success': True,
                    'message': 'Successfully logged out'
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'success': False,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response(
                {
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'success': False,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):

        try:
            profile = Profile.objects.select_related('user').get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile)

        return Response({
            'success': True,
            'data': serializer.data
        })


class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.select_related('user').get(user=request.user)
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile)
        return Response({
            'success': True,
            'data': serializer.data
        })

    def patch(self, request):
        try:
            profile = Profile.objects.select_related('user').get(user=request.user)
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
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
