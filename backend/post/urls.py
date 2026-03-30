from django.urls import path
from .views import PostCreateView, PostDetailView

urlpatterns = [
    path('posts/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

]