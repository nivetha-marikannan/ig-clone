from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProfileDetailView, ProfileUpdateView, RegisterView,
    FollowToggleView, FollowersListView, FollowingListView, FollowStatusView
)

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', ProfileUpdateView.as_view(), name='profile-me'),
    path('profile/<int:user_id>/', ProfileDetailView.as_view(), name='profile-detail'),
    
    path('follow/<int:user_id>/', FollowToggleView.as_view(), name='follow-toggle'),
    path('follow-status/<int:user_id>/', FollowStatusView.as_view(), name='follow-status'),
    path('<int:user_id>/followers/', FollowersListView.as_view(), name='followers-list'),
    path('<int:user_id>/following/', FollowingListView.as_view(), name='following-list'),
]
