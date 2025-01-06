from django.contrib import admin
from .models import BibleVerse, JournalEntry, Bookmark, Prayer, Like, PrayerTime

class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ('id','reference', 'verse_text', 'date', 'reflection')  # Add fields you want to display in the list view
    ordering = ['date']  # Use '-' to specify descending order

# Register the model with the custom admin
admin.site.register(BibleVerse, BibleVerseAdmin)

class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'title', 'created_date', 'content')
    ordering = ['created_date']

# Register the model with the custom admin (do it only once!)
admin.site.register(JournalEntry, JournalEntryAdmin)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'verse_reference', 'created_at')  # Customize columns
    list_filter = ('user',)  # Filter bookmarks by user
    search_fields = ('verse__verse_text', 'user__username')  # Search by verse text or user

    def verse_reference(self, obj):
        """Display verse reference instead of the verse object."""
        return f"{obj.verse.verse_text} - {obj.verse.reference}"
    verse_reference.short_description = 'Verse Reference'

class PrayersAdmin(admin.ModelAdmin):
    list_display = ('id','user','title', 'content', 'created_at')

# Register PrayersAdmin
admin.site.register(Prayer, PrayersAdmin)

class LikeVerse(admin.ModelAdmin):
    list_display = ('id', 'user', 'verse')

admin.site.register(Like, LikeVerse)


class PrayertimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prayer_time')

admin.site.register(PrayerTime, PrayertimeAdmin)
