from django.urls import path
from .views import PostCreateView, PostDetailView, CommentListCreateView, CommentDetailView, LikeListCreateView, LikeDetailView

urlpatterns = [
    path('posts/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
    path('posts/<int:post_id>/likes/', LikeListCreateView.as_view(), name='like-list-create'),
    path('posts/<int:post_id>/likes/<int:like_id>/', LikeDetailView.as_view(), name='like-detail'),
]