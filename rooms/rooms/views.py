from django.http import HttpResponseRedirect
from django.shortcuts import render

# Homepage render. Redirects to Raven if user is unauthenticated.

def get_home(request):
    if request.user.is_authenticated:
        return render(request, 'roomsurvey/index.html', { 'username' : request.user.get_short_name()})
    else:
        return HttpResponseRedirect('accounts/login')