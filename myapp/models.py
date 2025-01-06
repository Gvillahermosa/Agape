from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

# models.py

class BibleVerse(models.Model):
    reference = models.CharField(max_length=100)
    verse_text = models.TextField()
    date = models.DateField(default=timezone.now)
    reflection = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name="liked_verses", blank=True)
    mood = models.CharField(max_length=50, choices=[
        ('none','None'),
        ('angry', 'Angry'),
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('confused', 'Confused'),
        ('anxious','Anxious'),
        ('frustrated','Frustrated'),
        ('grateful','Grateful'),
        ('hopeful','Hopeful'),
        ('lonely','Lonely'),
        ('worried','Worried'),
        ('overwhelmed','Overwhelmed'),
    ],
    default='none',  # Set a default value
    null=False,  # Enforce a non-NULL value
    blank=True  # Allow blank values in forms
)

    def like_count(self):
        return self.likes.count()

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()

    def __str__(self):
        return f"{self.reference} - {self.date}"


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # This links each like to a user
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE)  # This links each like to a verse

    def __str__(self):
        return f"{self.user.username} liked: {self.verse.verse_text[:100]}..."  # First 50 characters of the verse_text

class JournalEntry(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_date = models.DateField()
    content = models.TextField()

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,default='../profile_pictures/account.png')

    def __str__(self):
        return self.user.username

class Bookmark(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'verse')  # Ensures a user can only bookmark a verse once

class Prayer(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prayers')  # Add ForeignKey to User

    def __str__(self):
        return self.title

class PrayerTime(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prayer_times')
    prayer_time = models.TimeField()

    def __str__(self):
        return f"{self.user.username} - {self.prayer_time}"



##################

class SharedVerse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verse = models.TextField()
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verse shared by {self.user.username} at {self.shared_at}"
