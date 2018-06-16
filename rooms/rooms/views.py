from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from roomsurvey.models import UserCompletedSurvey

# Homepage render. Redirects to Raven if user is unauthenticated.

def get_home(request):
    if request.user.is_authenticated:
        user_completed_survey = get_object_or_404(UserCompletedSurvey, user=request.user.get_username())
        if user_completed_survey.completed:
            return get_home_invalid(request)
        else:
            return render(request, 'roomsurvey/index.html', { 'username' : request.user.get_short_name()})
    else:
        return HttpResponseRedirect('accounts/login')


# Shown if the user has already completed the survey.

def get_home_invalid(request):
    text = """Sorry, looks like you've completed this survey already. Many thanks!"""
    return render(request, 'roomsurvey/error.html', { 'error' : text })