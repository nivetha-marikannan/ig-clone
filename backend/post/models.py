from django.db import models
from core.mixins import TimestampMixin, TimeStampWithUpdateMixin
from user.models import User
from django.conf import settings

class Post(TimeStampWithUpdateMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images/')
    caption = models.TextField(blank=True)
    hashtags = models.ManyToManyField('HashTag', blank=True, related_name='posts')

    def __str__(self):
        return f"Post - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class Like(TimestampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f"{self.user.username} likes Post {self.post.id}"

    class Meta:
        unique_together = ('user', 'post')

class Comment(TimeStampWithUpdateMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"
    
    class Meta:
        ordering = ['created_at']

class HashTag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

