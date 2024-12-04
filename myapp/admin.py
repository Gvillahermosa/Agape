from django.contrib import admin
from .models import BibleVerse, JournalEntry


class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ('reference', 'verse_text', 'date', 'reflection')  # Add fields you want to display in the list view
    ordering = ['date']  # Use '-' to specify descending order

# Register the model with the custom admin
admin.site.register(BibleVerse, BibleVerseAdmin)

class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user','title','created_date','content')
    ordering = ['created_date']

admin.site.register(JournalEntry, JournalEntryAdmin)
