# Generated by Django 4.2.4 on 2024-02-06 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniwallpapers', '0032_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallpapercollection',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
