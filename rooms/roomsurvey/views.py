from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Room, Staircase, SurveyResponse, Review
from .forms import StaircaseSelector, RoomSelector, SurveyForm

"""
VIEWS
Defines views to be used in this simple survey
application, to display various metadata.
"""

# Generic view to show room details.

class RoomDetailView(generic.DetailView):
    model = Room
    template_name = 'roomsurvey/room.html'


# Selector for staircase.

def get_staircase(request):
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
    staircase = get_object_or_404(Staircase, pk=staircase_id)
    if request.method == 'POST':
        form = RoomSelector(request.POST, staircase=s)
        if form.is_valid():
            room_id = request.POST.get('room')
            return HttpResponseRedirect('../../../roomsurvey/room_details/' + str(room_id))
    else:
        form = RoomSelector(staircase=s)
    return render(request, 'roomsurvey/get-room.html', {
        'form' : form,
        'staircase' : staircase,
        'username' : request.user.get_username()
    })


# Form to respond to survey.

def get_survey(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            review_text = request.POST.get('review')
            overpriced = request.POST.get('overpriced')
            
            # TODO: change form to allow selection of important factors.
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
            
            # TODO: redirect to confirmation page.
            return HttpResponseRedirect('#')
    else:
        form = SurveyForm()
    return render(request, 'roomsurvey/survey.html', {
        'form' : form,
        'room' : room,
        'username' : request.user.get_username()
    })