from .models import Profile

def profile_picture_processor(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            return {'profile_picture_url': profile.profile_picture.url}
        except Profile.DoesNotExist:
            return {'profile_picture_url': None}
    return {'profile_picture_url': None}
