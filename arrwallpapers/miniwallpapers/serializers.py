# from rest_framework import serializers
# from django.contrib.auth.models import User  
# from miniwallpapers.models import UserProfileDoc 

# class UserProfileSerializer(serializers.ModelSerializer):
#     # Define additional fields from the User model
#     username = serializers.ReadOnlyField(source='user.username')
#     email = serializers.ReadOnlyField(source='user.email')

#     class Meta:
#         model = UserProfileDoc
#         fields = ['username', 'email', 'phoneno', 'portfolio', 'is_approved']

from rest_framework import serializers
from miniwallpapers.models import UserProfileDoc

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    portfolio_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfileDoc
        fields = ['username', 'email', 'phoneno', 'portfolio', 'portfolio_url', 'is_approved', 'is_creator']

    def get_portfolio_url(self, obj):
        if obj.portfolio:
            # Assuming 'portfolio' is the name of the FileField
            return obj.portfolio.url
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.is_creator:
            # Remove is_creator from serialized data if it's False
            data.pop('is_creator')
        return data
