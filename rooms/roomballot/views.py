"""
VIEWS
Defines views to be used in this application.
Author Cameron O'Connor
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Room, Image, Staircase, Student, Syndicate
from django.conf import settings
from .methods import *
import json


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
    # If student already part of a syndicate, redirects to error page.
    if student.syndicate is not None:
        return error(request, 902)
    if request.method == 'POST':
        # TODO: implement some error handling here.
        usernames = request.POST.getlist('crsids[]')
        try:
            create_new_syndicate(usernames, request.user.username)
            response_code = 1
        except ConcurrencyException:
            response_code = 2
        return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
    else:
        student = Student.objects.get(user_id=request.user.username)
        return render(request, 'roomballot/create-syndicate.html', {'student': student,
                                                                    'students': Student.objects.filter(year=1, syndicate=None, in_ballot=True)})


# ============ SYNDICATE DETAIL ================
# Shows syndicate information, including allowing
# user to accept if required.

def syndicate_detail(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/roomballot')
    student = Student.objects.get(user_id=request.user.username)
    if request.method == 'POST':
        if request.POST.get('response') == '1':
            try:
                accept_syndicate(student)
                response_code = 1
            except ConcurrencyException:
                response_code = 2
        elif request.POST.get('response') == '2':
            decline_syndicate(student)
            response_code = 1
        elif request.POST.get('response') == '3':
            dissolve_syndicate(student.syndicate)
            response_code = 3
        else:
            response_code = 4
        return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
    else:
        if student.syndicate is None:
            return error(request, 903)
        students = []
        for st in Student.objects.filter(syndicate=student.syndicate).order_by('surname'):
            students.append(st)
        return render(request, 'roomballot/syndicate-view.html', {'student': student,
                                                                  'syndicate': student.syndicate,
                                                                  'students': students})


# ================= ERROR =====================
# Displays error page, with codes indicating the
# type of error.

def error(request, code):
    messages = {
        404: "Page not found",
        900: "Generic error.",
        901: "Concurrency error when creating syndicate.",
        902: "You're already part of a syndicate.",
        903: "You're not part of a syndicate.",
        904: "You're not registered as a student.",
        905: "You've already accepted this syndicate."
    }
    return render(request, 'roomballot/error.html', {'message': messages[code]})