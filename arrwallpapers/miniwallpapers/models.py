from django.db import models

# # Create your models here.
# class Creatorauth(models.Model):
#     username = models.CharField(max_length=50)
#     email = models.EmailField(max_length=100)
#     password = models.CharField(max_length=255)
#     portfolio = models.FileField(upload_to='portfolio')

from django.contrib.auth.models import User

class UserProfileDoc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    portfolio = models.FileField(upload_to='portfolio/', blank=True, null=True)

    def __str__(self):
        return self.user.username