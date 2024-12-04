from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path('', views.home, name="home"),
    path('', views.landing, name='landing'),
    path('findyourverse', views.findyourverse, name="findyourverse"),
    path('signup', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('journal', views.journal, name="journal"),
    path('viewjournal', views.viewjournal, name="viewjournal"),
    path('dailyverse', views.dailyverse, name="dailyverse"),
    path('bibleTriva', views.bibleTrivia, name="bibleTrivia"),
    path('delete_journal/<int:entry_id>/', views.delete_journal, name='delete_journal'),
    path('happyverses', views.happyverses, name="happyverses"),
    path('sadverse', views.sadverse, name="sadverse"),
    path('angryverse', views.angryverse, name="angryverse"),
    path('anxiousverse', views.anxiousverse, name="anxiousverse"),
    path('worriedverse', views.worriedverse, name="worriedverse"),
    path('gratefulverse', views.gratefulverse, name="gratefulverse"),
    path('frustratedverse', views.frustratedverse, name="frustratedverse"),
    path('lonelyverse', views.lonelyverse, name="lonelyverse"),
    path('hopefulverse', views.hopefulverse, name="hopefulverse"),
    path('overwhelmedverse', views.overwhelmedverse, name="overwhelmedverse"),
    path('confusedverse', views.confusedverse, name="confusedverse"),
    path('rosaryguide', views.rosaryguide, name="rosaryguide"),
    # path('rosary', views.rosary, name="rosary"),
    path('editProfile/', views.edit_profile, name='editProfile'),
    path('myLikes', views.myLikes, name='myLikes'),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
