# Generated by Django 4.2.3 on 2023-08-12 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miniwallpapers', '0002_alter_creatorauth_portfolio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creatorauth',
            name='portfolio',
            field=models.FileField(upload_to='portfolio'),
        ),
    ]
