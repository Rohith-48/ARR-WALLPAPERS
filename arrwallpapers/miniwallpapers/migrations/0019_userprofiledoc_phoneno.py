# Generated by Django 4.2.3 on 2023-09-24 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniwallpapers', '0018_userprofiledoc_subscribed'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofiledoc',
            name='phoneno',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
