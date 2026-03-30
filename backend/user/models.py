from django.db import models
from django.contrib.auth.models import AbstractUser
from core.mixins import TimestampMixin, TimeStampWithUpdateMixin
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)

    # password, username, is_active, is_staff, is_superuser, last_login, date_joined are inherited from AbstractUser
    
    USERNAME_FIELD = 'email' # this is for login with email instead of username
    REQUIRED_FIELDS = ['username'] # this is required for createsuperuser

    def __str__(self):
        return self.username
    
class Profile(TimestampMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile - {self.user.username}"
    
class Follow(TimestampMixin):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('follower', 'following')
        constraints = [ models.CheckConstraint(condition=~models.Q(follower=models.F('following')), name='prevent_self_follow') ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"