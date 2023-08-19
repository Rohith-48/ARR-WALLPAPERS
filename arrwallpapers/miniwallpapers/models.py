from django.db import models
from django.contrib.auth.models import User

class UserProfileDoc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    portfolio = models.FileField(upload_to='portfolio/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class WallpaperCollection(models.Model):
    WALLPAPER_PRICE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.CharField(max_length=10, choices=WALLPAPER_PRICE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None)
    tags = models.ManyToManyField(Tag, default=None)
    upload_date = models.DateTimeField(auto_now_add=True)
    wallpaper_image = models.ImageField(
        upload_to='wallpapers/',
        default='path_to_default_image.jpg',
    )

# Add default categories and tags
# Category.objects.get_or_create(name='hd')
# Category.objects.get_or_create(name='4k')

Tag.objects.get_or_create(name='superhero')
Tag.objects.get_or_create(name='nature')
Tag.objects.get_or_create(name='amoled')
