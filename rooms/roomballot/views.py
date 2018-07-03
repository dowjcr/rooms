"""
VIEWS
Defines views to be used in this application.
Author Cameron O'Connor
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Room, Image, Staircase, Student
from django.conf import settings


# ================ ROOM DETAIL ===================
# Displays room metadata.

def room_detail(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    room = get_object_or_404(Room, pk=room_id)
    total_price = room.price * room.staircase.contract_length / 100
    weekly_price = room.price / 100
    image_urls = []
    for image in Image.objects.filter(room=room):
        image_urls.append(settings.MEDIA_ROOT + image.file.url)
    occupant = None
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/room-detail-view.html', {'room': room,
                                                                'username': request.user.first_name,
                                                                'total_price': total_price,
                                                                'weekly_price': weekly_price,
                                                                'images': image_urls,
                                                                'student': student})


# =========== ROOM SELECTION CONFIRM ==============
# Prompts user to confirm that they have selected the
# correct room.

def room_selection_confirm(request, room_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    room = get_object_or_404(Room, pk=room_id)
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/room-select-confirm.html', {'room': room,
                                                                   'username': request.user.first_name,
                                                                   'student': student})


# =============== LANDING PAGE ===================
# Shown to user if they are not already authenticated
# using Raven.

def landing(request):
    if not request.user.is_authenticated:
        return render(request, 'roomballot/landing.html')
    else:
        return HttpResponseRedirect('/roomballot/dashboard')


# ============== STAIRCASE LIST ==================
# Lists all staircases, shows some metadata.

def staircase_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    return render(request, 'roomballot/staircase-list.html', {'staircases': Staircase.objects.order_by('name'),
                                                              'username': request.user.first_name})


# ============= STAIRCASE DETAIL =================
# Shows staircase metadata, and all rooms on this
# given staircase.

def staircase_detail(request, staircase_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    staircase = get_object_or_404(Staircase, pk=staircase_id)
    return render(request, 'roomballot/staircase-view.html', {'staircase': staircase,
                                                              'rooms': Room.objects.filter(staircase=staircase).order_by('room_number'),
                                                              'username': request.user.first_name},)


# ============ STUDENT DASHBOARD =================
# Account dashboard for student. Displays current
# room selection status, syndicate status etc.

def student_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    student = Student.objects.get(user_id=request.user.username)
    room = None
    if student.has_allocated:
        room = Room.objects.get(taken_by=student)
    # TODO: make this throw an error if student not in table.
    # TODO: deal with edge case of admin (Beverley).
    return render(request, 'roomballot/dashboard-student.html', {'student': student,
                                                                 'username': request.user.first_name,
                                                                 'room': room})


# ============ CREATE SYNDICATE ================
# Allows user to create a new syndicate.

def create_syndicate(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/create-syndicate.html', {'student': student,
                                                                'students': Student.objects.filter(year=1, syndicate=None, in_ballot=True)})


# ================= ERROR =====================
# Displays error page, with codes indicating the
# type of error.

def error(request, code):
    messages = {
        404: "Page not found",
        901: "Concurrency error when creating syndicate."
    }
    return render(request, 'roomballot/error.html', {'message': messages[code]})