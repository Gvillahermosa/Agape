from django.shortcuts import redirect, render
import logging
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import BibleVerse, JournalEntry, Profile, Like, BibleVerse, SharedVerse, Bookmark,Prayer,PrayerTime
from django.utils import timezone
import random
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from random import sample
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt


VERSES = [
    "Trust in the LORD with all your heart. - Proverbs 3:5",
    "The Lord is my shepherd; I shall not want. - Psalm 23:1",
    "I can do all things through Christ. - Philippians 4:13",
    "Be strong and courageous. - Joshua 1:9",
    "Cast all your anxiety on Him. - 1 Peter 5:7",
    "The LORD is my light and my salvation. - Psalm 27:1",
    "The name of the LORD is a strong tower. - Proverbs 18:10",
    "Do not be anxious about anything. - Philippians 4:6",
    "I will fear no evil, for You are with me. - Psalm 23:4",
    "Pray without ceasing. - 1 Thessalonians 5:17",
    "The peace of God will guard your hearts. - Philippians 4:7",
    "The Lord is good to all. - Psalm 145:9",
    "God is love. - 1 John 4:8"
]


#MAINPAGE

def landing(request):
    fname = request.session.get('fname')  # Retrieve first name from session
    return render(request, 'html/landing.html', {'fname': fname})

@login_required
def findyourverse(request):
    fname = request.session.get('fname')
    verse = random.choice(VERSES)
    return render(request, "html/findverse.html", {'fname': fname, 'verse': verse})

@login_required
def journal(request):
    if request.method == "POST":
        title = request.POST.get('title')
        created_date = request.POST.get('created_date') or timezone.now().date()
        content = request.POST.get('content')

        JournalEntry.objects.create(
            user=request.user,
            title=title,
            created_date=created_date,
            content=content
        )
        response = redirect('journal')  # Redirect to view notes page after saving
        response.set_cookie('journal_added', 'true', max_age=5)  # Set a temporary cookie
        return response

    fname = request.session.get('fname')
    return render(request, "html/journal.html",  {'fname': fname})


# views.py
@login_required
def viewjournal(request):
    fname = request.session.get('fname')
    query = request.GET.get('q', '')  # Fetch search query from the URL

    if query:
        journal_entries = JournalEntry.objects.filter(user=request.user, title__icontains=query)
    else:
        journal_entries = JournalEntry.objects.filter(user=request.user)

    total_entries = journal_entries.count()  # Count the entries

    return render(request, "html/viewnotes.html", {
        'fname': fname,
        'journal_entries': journal_entries,
        'query': query,
        'total_entries': total_entries
    })



@login_required
def delete_journal(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    entry.delete()

    response = redirect('viewjournal')
    response.set_cookie('journal_deleted', 'true', max_age=5)  # Set a temporary cookie for deletion
    return response

def dailyverse(request):
    fname = request.session.get('fname')
    today = timezone.now().date()  # Get today's date
    verse = BibleVerse.objects.filter(date=today).first()

    # Combine the context into a single dictionary
    context = {
        'fname': fname,
        'verse': verse,
    }

    return render(request, "html/daily-verse.html", context)


def bibleTrivia(request):
    fname = request.session.get('fname')
    return render(request, "html/bibleTrivia.html", {'fname': fname})

@login_required  # Ensure the user is logged in
def customprayers(request):
    if request.method == "POST":
        # Get data from the submitted form
        prayer_title = request.POST.get('prayer_title')
        prayer_text = request.POST.get('prayer_text')

        # Save to the database
        if prayer_title and prayer_text:  # Ensure both fields are provided
            Prayer.objects.create(title=prayer_title, content=prayer_text, user=request.user)  # Link prayer to user

        # Redirect to the prayer list
        return redirect('viewcustomprayers')  # Replace with the name of your URL for the prayer list

    # For GET requests, show the "Add Prayer" form
    fname = request.session.get('fname')
    return render(request, "html/custom_prayers.html", {'fname': fname})


@login_required  # Ensure the user is logged in
def viewcustomprayers(request):
    fname = request.session.get('fname')
    prayers = Prayer.objects.filter(user=request.user)  # Filter prayers by the logged-in user
    return render(request, "html/view_custom_prayers.html", {'prayers': prayers, 'fname': fname})

def setTime(request):
    if request.method == 'POST':
        prayer_time = request.POST.get('prayer_time')
        # Create or update the user's prayer time
        PrayerTime.objects.update_or_create(user=request.user, defaults={'prayer_time': prayer_time})
        return redirect('setTime')  # Redirect to the same page or wherever appropriate

    # Fetch existing prayer times
    prayer_times = PrayerTime.objects.filter(user=request.user)
    return render(request, 'html/set_time.html', {'prayer_times': prayer_times})


# View to handle deletion of a prayer
@csrf_exempt  # This is temporary; ensure proper CSRF handling for production
def delete_prayer(request, id):
    prayer = get_object_or_404(Prayer, id=id)  # Retrieve the prayer by ID

    if request.method == "POST":
        prayer.delete()  # Delete the prayer
        return JsonResponse({'status': 'success'})  # Respond with success
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.user.username = request.POST.get('username')
        profile.user.first_name = request.POST.get('first_name')
        profile.user.last_name = request.POST.get('last_name')
        profile.user.email = request.POST.get('email')

        # Handle password change
        if request.POST.get('password'):
            profile.user.set_password(request.POST.get('password'))

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.user.save()
        profile.save()

        # Store first name in session
        request.session['fname'] = profile.user.first_name

        return redirect('landing')

    return render(request, 'html/editProfile.html', {'profile': profile})



logger = logging.getLogger(__name__)

@login_required
def myLikes(request):
    if request.method == "GET":
        user = request.user
        bookmarks = Bookmark.objects.filter(user=user).select_related('verse')
        return render(request, 'html/myLikes.html', {'bookmarks': bookmarks})

    elif request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            bookmark_id = data.get('bookmark_id')
            if not bookmark_id:
                logger.warning("No bookmark ID provided in deletion request.")
                return JsonResponse({'success': False, 'error': 'No bookmark ID provided.'}, status=400)

            bookmark = get_object_or_404(Bookmark, id=bookmark_id, user=request.user)
            bookmark.delete()
            logger.info(f"Bookmark with ID {bookmark_id} deleted by user {request.user.username}.")
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            logger.error("Invalid JSON data received for bookmark deletion.")
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            logger.exception("An unexpected error occurred while deleting a bookmark.")
            return JsonResponse({'success': False, 'error': 'An error occurred while deleting the bookmark.'}, status=500)

    logger.warning("Invalid request method attempted on myLikes view.")
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


@login_required
def share_verse(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            verse = data.get('verse')

            if verse:  # Check if verse is provided
                # Save the shared verse in the database
                SharedVerse.objects.create(user=request.user, verse=verse)
                return JsonResponse({'success': True, 'message': 'Verse shared successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'No verse provided!'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data!'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def rosaryguide(request):
    fname = request.session.get('fname')
    return render(request, "html/rosaryguide.html", {'fname': fname})

#LOGIN AND SIGNUP
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
import re

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        context = {
                'username': username,
                'fname': fname,
                'lname': lname,
                'email': email,
                'show_signup': True  # Add this line
            }

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.", extra_tags='signup')

            return render(request, "html/index.html", context)

          # Validate password length
        if len(pass1) < 8 and len(pass2) < 8:
            messages.error(request, "Password must be at least 8 characters long.", extra_tags='signup')
            return render(request, "html/index.html", context)

        # Check if password is all numbers
        if pass1.isdigit() and pass2.isdigit():
            messages.error(request, "Password must not consist of only numbers.", extra_tags='signup')
            return render(request, "html/index.html", context)

        # Check if password contains at least one letter
        if not re.search(r'[a-zA-Z]', pass1):
            messages.error(request, "Password must contain at least one letter.", extra_tags='signup')
            return render(request, "html/index.html", context)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.", extra_tags='signup')
            return render(request, "html/index.html", context)

        # Optional: Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered. Please use a different email.", extra_tags='signup')
            return render(request, "html/index.html", context)


        # Create the user if passwords match
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your account has been successfully created.", extra_tags='signup')
        return redirect('signin')

    # If GET request, show the sign-up form
    return render(request, "html/index.html", {'show_signup': True})


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        # Check if the username exists in the database
        user_exists = User.objects.filter(username=username).exists()

        if user_exists:
            # If the username exists, check if the password is correct
            user = authenticate(username=username, password=pass1)
            if user is not None:
                login(request, user)
                # Get the 'next' parameter from the request
                next_url = request.GET.get('next')  # 'next' is passed automatically when using @login_required
                if next_url:
                    return redirect(next_url)  # Redirect to the original page
                else:
                    request.session['fname'] = user.first_name  # Store first name in session
                    return redirect('landing')  # Default redirect if no 'next' is provided
            else:
                # Password is incorrect
                messages.error(request, "Password is not correct", extra_tags='signin')
        else:
            # Username is incorrect
            messages.error(request, "Username is not correct", extra_tags='signin')

        context = {'show_signup': False}
        return render(request, "html/index.html", context)

    return render(request, "html/index.html", {'show_signup': False})

def signout(request):
    logout(request)
    response = redirect('landing')
    response.set_cookie('logout_success', 'true', max_age=5)  # Cookie expires after 5 seconds
    return response



#For the feelings
@login_required
def happyverses(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    happy_verses = BibleVerse.objects.filter(mood='happy').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in happy_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/happy.html", {
        'fname': fname,
        'happy_verses': happy_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })



@login_required
def sadverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    sad_verses = BibleVerse.objects.filter(mood='sad').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in sad_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/sad.html", {
        'fname': fname,
        'sad_verses': sad_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })



@login_required
def angryverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    angry_verses = BibleVerse.objects.filter(mood='angry').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in angry_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/angry.html", {
        'fname': fname,
        'angry_verses': angry_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })



@login_required
def anxiousverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    anxious_verses = BibleVerse.objects.filter(mood='anxious').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in anxious_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/anxious.html", {
        'fname': fname,
        'anxious_verses': anxious_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })



@login_required
def worriedverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    worried_verses = BibleVerse.objects.filter(mood='worried').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in worried_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/worried.html", {
        'fname': fname,
        'worried_verses': worried_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })


@login_required
def gratefulverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    grateful_verses = BibleVerse.objects.filter(mood='grateful').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in grateful_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/grateful.html", {
        'fname': fname,
        'grateful_verses': grateful_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })


@login_required
def frustratedverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    frustrated_verses = BibleVerse.objects.filter(mood='frustrated').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in frustrated_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/frustrated.html", {
        'fname': fname,
        'frustrated_verses': frustrated_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })

@login_required
def lonelyverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    lonely_verses = BibleVerse.objects.filter(mood='lonely').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in lonely_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/lonely.html", {
        'fname': fname,
        'lonely_verses': lonely_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })


@login_required
def hopefulverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    hopeful_verses = BibleVerse.objects.filter(mood='hopeful').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in hopeful_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/hopeful.html", {
        'fname': fname,
        'hopeful_verses': hopeful_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })


@login_required
def overwhelmedverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    overwhelmed_verses = BibleVerse.objects.filter(mood='overwhelmed').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in overwhelmed_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/overwhelmed.html", {
        'fname': fname,
        'overwhelmed_verses': overwhelmed_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })
@login_required
def confusedverse(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        verse_id = data.get('verse_id')
        action = data.get('action')  # 'like', 'unlike', 'bookmark', 'unbookmark'

        if verse_id and action:
            try:
                verse = BibleVerse.objects.get(id=verse_id)

                # Handle 'like' and 'unlike' actions
                if action == 'like':
                    Like.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unlike':
                    Like.objects.filter(user=request.user, verse=verse).delete()

                # Handle 'bookmark' and 'unbookmark' actions
                elif action == 'bookmark':
                    Bookmark.objects.get_or_create(user=request.user, verse=verse)
                elif action == 'unbookmark':
                    Bookmark.objects.filter(user=request.user, verse=verse).delete()

                # Return updated like and bookmark count
                like_count = Like.objects.filter(verse=verse).count()
                bookmark_count = Bookmark.objects.filter(verse=verse).count()
                return JsonResponse({'success': True, 'like_count': like_count, 'bookmark_count': bookmark_count})
            except BibleVerse.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Verse not found'})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

    # Standard GET request handling
    fname = request.session.get('fname')

    # Randomize the verses
    confused_verses = BibleVerse.objects.filter(mood='confused').order_by('?')

    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)
    bookmarked_verses = Bookmark.objects.filter(user=request.user).values_list('verse', flat=True)

    for verse in confused_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()
        verse.bookmark_count = Bookmark.objects.filter(verse=verse).count()

    return render(request, "feelings/confused.html", {
        'fname': fname,
        'confused_verses': confused_verses,
        'liked_verses': liked_verses,
        'bookmarked_verses': bookmarked_verses
    })
