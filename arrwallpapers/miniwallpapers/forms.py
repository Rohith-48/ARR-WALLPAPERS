# from django import forms
# from .models import WallpaperCollection

# class UploadWallpaperForm(forms.ModelForm):
#     class Meta:
#         model = WallpaperCollection
#         fields = ['title', 'description', 'price', 'category', 'tags', 'wallpaper_image']
# forms.py
# from django import forms
# from .models import Comment

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['text']

from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class LoginForm(forms.Form):
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def clean_recaptcha(self):
        recaptcha_response = self.cleaned_data.get('recaptcha')
        if not recaptcha_response:
            raise forms.ValidationError("Please complete the reCAPTCHA verification.")
        return recaptcha_response
