# Generated by Django 4.2.4 on 2024-02-12 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniwallpapers', '0037_remove_chatmessage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat_images/'),
        ),
    ]
