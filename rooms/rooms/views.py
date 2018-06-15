from django.http import HttpResponseRedirect

# Homepage render. Redirects to Raven if user is unauthenticated.

def get_home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/roomsurvey/home')
    else:
        return HttpResponseRedirect('accounts/login')