from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import BibleVerse, JournalEntry
from django.utils import timezone
import random
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import SharedVerse
import json
from .models import Profile, Like, BibleVerse


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
        return redirect('journal')  # Redirect to view notes page after saving

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
    return redirect('viewjournal')

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
    return render(request, "html/bibleTrivia.html")


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)  # Create profile if it doesn't exist

    if request.method == 'POST':
        profile.user.username = request.POST.get('username')
        profile.user.first_name = request.POST.get('first_name')
        profile.user.last_name = request.POST.get('last_name')
        profile.user.email = request.POST.get('email')

        # Handle password change
        if request.POST.get('password'):
            profile.user.set_password(request.POST.get('password'))

        # Handle profile picture upload
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES.get('profile_picture')

        profile.user.save()
        profile.save()
        return redirect('landing')  # Redirect to the profile page

    return render(request, 'html/editProfile.html', {'profile': profile})



def myLikes(request):
    return render(request, "html/myLikes.html")


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
    messages.success(request, "Log out successfully")
    return redirect('landing')



#For the feelings

def happyverses(request):
    fname = request.session.get('fname')
    return render(request, "feelings/happy.html", {'fname': fname})


def sadverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/sad.html", {'fname': fname})

@login_required
def angryverse(request):
    fname = request.session.get('fname')
    angry_verses = BibleVerse.objects.filter(mood='angry')  # Filter angry verses
    liked_verses = Like.objects.filter(user=request.user).values_list('verse', flat=True)  # Get the liked verses for the user

    if request.method == "POST":
        verse_id = request.POST.get('verse_id')  # Get the verse ID from the submitted form
        verse = BibleVerse.objects.get(id=verse_id)  # Retrieve the verse object

        # Check if the user has already liked the verse
        if verse.id not in liked_verses:
            # If the user has not liked it, create a like
            Like.objects.create(user=request.user, verse=verse)
        else:
            # If the user has already liked it, delete the like (unlike)
            Like.objects.filter(user=request.user, verse=verse).delete()

        return redirect('angryverse')  # Redirect to the same page to avoid form resubmission

    # Fetch the number of likes for each verse
    for verse in angry_verses:
        verse.like_count = Like.objects.filter(verse=verse).count()

    # Render the page with the verses, liked verses, and like counts
    return render(request, "feelings/angry.html", {'fname': fname, 'angry_verses': angry_verses, 'liked_verses': liked_verses})

def anxiousverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/anxious.html", {'fname': fname})

def worriedverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/worried.html", {'fname': fname})

def gratefulverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/grateful.html", {'fname': fname})

def frustratedverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/frustrated.html", {'fname': fname})

def lonelyverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/lonely.html", {'fname': fname})

def hopefulverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/hopeful.html", {'fname': fname})

def overwhelmedverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/overwhelmed.html", {'fname': fname})

def confusedverse(request):
    fname = request.session.get('fname')
    return render(request, "feelings/confused.html", {'fname': fname})
