# Generated by Django 4.2.7 on 2024-12-03 05:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0004_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='bibleverse',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_verses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bibleverse',
            name='mood',
            field=models.CharField(blank=True, choices=[('none', 'None'), ('angry', 'Angry'), ('happy', 'Happy'), ('sad', 'Sad'), ('confused', 'Confused'), ('anxious', 'Anxious'), ('frustrated', 'Frustrated'), ('grateful', 'Grateful'), ('hopeful', 'Hopeful'), ('lonely', 'Lonely'), ('worried', 'Worried'), ('overwhelmed', 'Overwhelmed')], default='none', max_length=50),
        ),
    ]
