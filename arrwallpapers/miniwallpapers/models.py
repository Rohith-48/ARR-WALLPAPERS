from django.db import models
from django.contrib.auth.models import User

class UserProfileDoc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)  
    is_premium = models.BooleanField(default=False) 
    is_approved = models.BooleanField(default=False)
    portfolio = models.FileField(upload_to='portfolio/', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    about_me = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username
    
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Tag(models.Model):
    name = models.CharField(max_length=50)
    hashtag = models.CharField(max_length=50, default='default_hashtag') 

    def __str__(self):
        return f'#{self.name}'

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('superhero', 'Superhero'),
        ('movie', 'Movie'),
        ('nature', 'Nature'),
        ('wildlife', 'Wildlife'),
        ('cars', 'Cars'),
        ('bikes', 'Bikes'),
        ('ai_arts', 'AI Arts'),
        ('others', 'Others'),
    ]

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='others')

    def __str__(self):
        return self.get_name_display()

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
    is_superuser = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    wallpaper_image = models.ImageField(
        upload_to='wallpapers/',
        default='path_to_default_image.jpg',
    )

    def clean(self):
        if self.tags.count() > 4:
            raise ValidationError("A wallpaper can have a maximum of 4 tags.")
