from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from nltk.sentiment import SentimentIntensityAnalyzer
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount

class UserProfileDoc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    subscribed = models.BooleanField(default=False)
    subscription_expiration = models.DateField(null=True, blank=True)
    subscription_duration = models.PositiveIntegerField(default=0)
    portfolio = models.FileField(upload_to='portfolio/', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    about_me = models.TextField(blank=True)
    phoneno = models.CharField(max_length=15, blank=True, null=True)
    money = models.IntegerField(default=0)

    @classmethod
    def get_or_create_profile(cls, user):
        profile, created = cls.objects.get_or_create(user=user)
        return profile

    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=50)
    hashtag = models.CharField(max_length=50, default='default_hashtag')

    def __str__(self):
        return f'#{self.name}'

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('superhero', 'Superhero'),
        ('anime', 'Anime'),
        ('movie', 'Movie'),
        ('nature', 'Nature'),
        ('game', 'Game'),
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

    def get_upload_path(instance, filename):
        category_folder = instance.category.name.lower().replace(" ", "_")
        return f'wallpapers/{category_folder}/{filename}'

    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.CharField(max_length=10, choices=WALLPAPER_PRICE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None)
    tags = models.ManyToManyField(Tag, default=None)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    sentiment_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    wallpaper_image = models.ImageField(
        upload_to=get_upload_path,
        default='path_to_default_image.jpg',
    )
    downloads_by_user = models.ManyToManyField(User, related_name='downloads', blank=True)



    def download(self, user):
        if self.price == 'paid' and user.userprofiledoc.subscribed:
            if user in self.downloads_by_user.all():
                # User has already downloaded this wallpaper, no additional earning
                pass
            else:
                # Increment the download count for the wallpaper
                self.downloads += 1
                self.downloads_by_user.add(user)
                self.save()

                # Increment the creator's earnings
                self.user.userprofiledoc.money += 5.00
                self.user.userprofiledoc.save()

        # Additional logic for handling the download
        # ...

    def __str__(self):
        return self.title

    def clean(self):
        if self.tags.count() > 4:
            raise ValidationError("A wallpaper can have a maximum of 4 tags.")

    def update_average_rating(self):
        # Calculate the new average rating whenever a new rating is added
        ratings = Rating.objects.filter(wallpaper=self)
        total_ratings = ratings.count()
        if total_ratings > 0:
            average_rating = ratings.aggregate(models.Avg('value'))['value__avg']
            self.average_rating = round(average_rating, 2)
        else:
            self.average_rating = 0.00
        self.total_ratings = total_ratings
        self.save()

    def calculate_sentiment_score(self):
        reviews_text = ' '.join([review.text for review in self.review_set.all()])
        if reviews_text:
            sid = SentimentIntensityAnalyzer()
            sentiment_score = sid.polarity_scores(reviews_text)['compound']
            self.sentiment_score = round(sentiment_score, 2)
        else:
            self.sentiment_score = 0.00

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_sentiment_score()

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallpaper = models.ForeignKey(WallpaperCollection, on_delete=models.CASCADE)
    value = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the average rating and total ratings for the associated wallpaper
        self.wallpaper.update_average_rating()

    def __str__(self):
        return f"{self.user.username} - {self.wallpaper.title} - {self.value}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallpaper = models.ForeignKey(WallpaperCollection, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.wallpaper.calculate_sentiment_score()

    def __str__(self):
        return f"{self.user.username} - {self.wallpaper.title}"



from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'
