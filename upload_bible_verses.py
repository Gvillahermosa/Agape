import os
import pandas as pd
import django
from django.conf import settings

# Set the Django settings module before importing Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agape.settings')  # Change 'Agape.settings' to your project's settings module
django.setup()  # Initialize Django

from myapp.models import BibleVerse  # Adjust the import based on your app name

def upload_bible_verses(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Iterate through each row in the DataFrame and create BibleVerse objects
    for index, row in df.iterrows():
        BibleVerse.objects.create(
            reference=row['reference'],  # Replace with the actual column name
            verse_text=row['verse_text'],  # Replace with the actual column name
            date=row['date'],  # Replace with the actual column name or leave as default
            reflection=row.get('reflection', '')  # Replace with the actual column name or leave blank
        )

    print('Successfully uploaded Bible verses')

if __name__ == '__main__':
    # Use a raw string or forward slashes to specify your file path
    file_path = r'C:\Users\admin\Desktop\Agape\DailyBibleverses.xlsx'
    upload_bible_verses(file_path)
