from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Room, Staircase
from .forms import StaircaseSelector, RoomSelector

"""
VIEWS
Defines views to be used in this simple survey
application, to display various metadata.
"""

## Generic view to show room details.

class RoomDetailView(generic.DetailView):
    model = Room
    template_name = 'roomsurvey/room.html'


## Selector for staircase.

def get_staircase(request):
    if request.method == 'POST':
        form = StaircaseSelector(request.POST)
        if form.is_valid():
            id = request.POST.get('staircase')
            return HttpResponseRedirect('/roomsurvey/staircase/' + str(id) + '/selectroom')

    else:
        form = StaircaseSelector()

    return render(request, 'roomsurvey/get-staircase.html', {'form': form})


## Selector for room, reactive to previous staircase selection.
## TODO - implement reaction.

def get_room(request, staircase_id):
    st = get_object_or_404(Staircase, pk=staircase_id)
    if request.method == 'POST':
        form = RoomSelector(request.POST)
        if form.is_valid():
            id = request.POST.get('room')
            return HttpResponseRedirect('../../../roomsurvey/room_details/' + str(id))
    
    else:
        form = RoomSelector()
    
    return render(request, 'roomsurvey/get-room.html', {
        'form' : form,
        'staircase' : st
    })
