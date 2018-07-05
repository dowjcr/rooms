from django.http import HttpResponseRedirect

# Homepage render. Redirects to Raven if user is unauthenticated.

def get_home(request):
    return HttpResponseRedirect('/roomballot/dashboard')