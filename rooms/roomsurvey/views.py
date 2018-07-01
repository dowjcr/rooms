from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Room, Staircase, SurveyResponse, Review, UserCompletedSurvey
from .forms import StaircaseSelector, RoomSelector, SurveyForm

"""
VIEWS
Defines views to be used in this simple survey
application, to display various metadata.
"""

# Shows room details.

def show_room(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')
    room = get_object_or_404(Room, pk=room_id)
    if room.survey_completed:
        # TODO: create error page, saying survey already conducted for that room.
        return get_room_invalid(request)
    else:
        return render(request, 'roomsurvey/room.html', { 'room' : room })


# Selector for staircase.

def get_staircase(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')
    if request.method == 'POST':
        form = StaircaseSelector(request.POST)
        if form.is_valid():
            staircase_id = request.POST.get('staircase')
            return HttpResponseRedirect('/roomsurvey/staircase/' + str(staircase_id) + '/selectroom')
    else:
        form = StaircaseSelector()
    return render(request, 'roomsurvey/get-staircase.html', {'form': form})


# Selector for room, reactive to previous staircase selection.

def get_room(request, staircase_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('../../../accounts/login')
    staircase = get_object_or_404(Staircase, pk=staircase_id)
    if request.method == 'POST':
        form = RoomSelector(request.POST, staircase=staircase)
        if form.is_valid():
            room_id = request.POST.get('room')
            return HttpResponseRedirect('../../../roomsurvey/room_details/' + str(room_id))
    else:
        form = RoomSelector(staircase=staircase)
    return render(request, 'roomsurvey/get-room.html', {
        'form' : form,
        'staircase' : staircase,
        'username' : request.user.get_username()
    })


# Form to respond to survey.

def get_survey(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('../../accounts/login')
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            review_text = request.POST.get('review')
            overpriced = request.POST.get('overpriced')
            
            # TODO: change form to allow selection of important factors.
            # TODO: change to use sanitised values.
            important_factors = 'hey'

            # Create Review object.
            review = Review()
            review.author = request.user.get_username()
            review.room = room
            review.text = review_text
            review.save()
            
            # Create SurveyResponse object.
            response = SurveyResponse()
            response.author = request.user.get_username()
            response.room = room
            response.review = review
            response.overpriced = overpriced
            response.important_factors = important_factors
            response.save()

            # Mark room as having been surveyed.
            room.survey_completed = True
            room.save()

            # Mark user as having completed survey.
            user_completed_survey = get_object_or_404(UserCompletedSurvey, user=request.user.get_username())
            user_completed_survey.completed = True
            user_completed_survey.save()
            
            # TODO: redirect to confirmation page.
            return HttpResponseRedirect('../confirmation')
    else:
        form = SurveyForm()
    return render(request, 'roomsurvey/survey.html', {
        'form' : form,
        'room' : room,
        'username' : request.user.get_username()
    })


# Confirmation page after completing survey.

def get_confirmation(request):
    return render(request, 'roomsurvey/confirmation.html')


# Shown if survey has already been completed for that room.

def get_room_invalid(request):
    text = """Sorry, the survey has already been completed for this room. Did you
    definitely select the right room?"""
    return render(request, 'roomsurvey/error.html', { 'error' : text })
