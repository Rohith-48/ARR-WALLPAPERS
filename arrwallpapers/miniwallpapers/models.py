from django.db import models
from django.contrib.auth.models import User

class UserProfileDoc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    portfolio = models.FileField(upload_to='portfolio/', blank=True, null=True)

    def __str__(self):
        return self.user.username