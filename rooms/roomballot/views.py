"""
VIEWS
Defines views to be used in this application.
Author Cameron O'Connor
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings as django_settings
from .models import *
from .methods import *
from modeldict import ModelDict
import json

settings = ModelDict(Setting, key='key', value='value', instances=False)


# ================ ROOM DETAIL ===================
# Displays room metadata.

def room_detail(request, room_id):
    student = Student.objects.get(user_id=request.user.username)
    room = get_object_or_404(Room, pk=room_id)
    reviews = Review.objects.filter(room=room)
    selectable = settings['ballot_in_progress'] == 'true' and settings['current_student'] == request.user.username
    total_price = room.price * room.staircase.contract_length / 100
    weekly_price = room.price / 100
    image_urls = []
    for image in Image.objects.filter(room=room):
        image_urls.append('https://ballot.downingjcr.co.uk/media/' + image.file.url)        # TODO - change this link.
    return render(request, 'roomballot/room-detail-view.html', {'room': room,
                                                                'total_price': total_price,
                                                                'weekly_price': weekly_price,
                                                                'images': image_urls,
                                                                'student': student,
                                                                'reviews': reviews,
                                                                'selectable': selectable})


# =========== ROOM SELECTION CONFIRM ==============
# Prompts user to confirm that they have selected the
# correct room.

def room_selection_confirm(request, room_id):
    student = Student.objects.get(user_id=request.user.username)
    room = get_object_or_404(Room, pk=room_id)
    can_allocate = settings['ballot_in_progress'] == 'true' and settings['current_student'] == request.user.username
    if request.method == 'POST':
        try:
            if student.syndicate is None or not student.accepted_syndicate or not student.syndicate.complete:
                raise ConcurrencyException()
            else:
                if can_allocate:
                    allocate_room(room, student)
                    response_code = 1
                else:
                    response_code = 404
        except ConcurrencyException:
            response_code = 900
        return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
    else:
        if can_allocate:
            return render(request, 'roomballot/room-select-confirm.html', {'room': room,
                                                                           'student': student})
        else:
            return error(request, 404)


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
    student = Student.objects.get(user_id=request.user.username)
    staircases = Staircase.objects.order_by('name')
    # Getting metadata
    class ModifiedStaircase(object):
        pass

    modified_staircases = []
    for staircase in staircases:
        rooms = Room.objects.filter(staircase=staircase)
        total_rooms = rooms.count()
        available_rooms = rooms.filter(taken_by=None).count()
        ms = ModifiedStaircase()
        ms.name = staircase.name
        ms.total_rooms = total_rooms
        ms.available_rooms = available_rooms
        ms.staircase_id = staircase.staircase_id
        modified_staircases.append(ms)
    return render(request, 'roomballot/staircase-list.html', {'staircases': modified_staircases,
                                                              'student': student})


# ============= STAIRCASE DETAIL =================
# Shows staircase metadata, and all rooms on this
# given staircase.

def staircase_detail(request, staircase_id):
    student = Student.objects.get(user_id=request.user.username)
    staircase = get_object_or_404(Staircase, pk=staircase_id)
    try:
        floorplan = Floorplan.objects.get(staircase=staircase)
    except:
        floorplan = None
    return render(request, 'roomballot/staircase-view.html', {'staircase': staircase,
                                                              'rooms': Room.objects.filter(staircase=staircase)
                                                                                   .order_by('sort_number'),
                                                              'floorplan': floorplan,
                                                              'student': student})


# ============ STUDENT DASHBOARD =================
# Account dashboard for student. Displays current
# room selection status, syndicate status etc.

def student_dashboard(request):
    student = Student.objects.get(user_id=request.user.username)
    room = Room.objects.get(taken_by=student) if student.has_allocated else None
    can_pick = settings['current_student'] == request.user.username and settings['ballot_in_progress'] == 'true'
    return render(request, 'roomballot/dashboard-student.html', {'student': student,
                                                                 'room': room,
                                                                 'can_pick': can_pick})


# ============ CREATE SYNDICATE ================
# Allows user to create a new syndicate.

def create_syndicate(request):
    try:
        student = Student.objects.get(user_id=request.user.username)
        # If student already part of a syndicate, redirects to error page.
        if student.syndicate is not None:
            return error(request, 902)
        # If student in second year, redirects to error page.
        if student.year == 2:
            return error(request, 403)
        if request.method == 'POST':
            usernames = request.POST.getlist('crsids[]')
            try:
                create_new_syndicate(usernames, request.user.username)
                response_code = 1
            except ConcurrencyException:
                response_code = 901
            except BallotInProgressException:
                response_code = 907
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            student = Student.objects.get(user_id=request.user.username)
            return render(request, 'roomballot/create-syndicate.html', {'student': student,
                                                                        'students': Student.objects.filter(year=1,
                                                                                                           syndicate=None,
                                                                                                           in_ballot=True)})
    except BallotInProgressException:
        return error(request, 907)


# ============ SYNDICATE DETAIL ================
# Shows syndicate information, including allowing
# user to accept if required.

def syndicate_detail(request):
    student = Student.objects.get(user_id=request.user.username)
    if request.method == 'POST':
        if request.POST.get('response') == '1':
            try:
                accept_syndicate(student)
                response_code = 1
            except ConcurrencyException:
                response_code = 905
        elif request.POST.get('response') == '2':
            try:
                decline_syndicate(student)
                response_code = 1
            except ConcurrencyException:
                response_code = 905
        elif request.POST.get('response') == '3':
            dissolve_syndicate(student.syndicate)
            response_code = 2
        else:
            response_code = 900
        return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
    else:
        if student.syndicate is None:
            return error(request, 903)
        students = []
        for s in Student.objects.filter(syndicate=student.syndicate).order_by('surname'):
            students.append(s)
        return render(request, 'roomballot/syndicate-view.html', {'student': student,
                                                                  'syndicate': student.syndicate,
                                                                  'students': students})


# ================= ERROR =====================
# Displays error page, with codes indicating the
# type of error.

def error(request, code):
    messages = {
        403: "Access Denied",
        404: "Page not found",
        900: "Generic error.",
        901: "Concurrency error when creating syndicate.",
        902: "You're already part of a syndicate.",
        903: "You're not part of a syndicate.",
        904: "You're not registered as a student.",
        905: "You've already accepted this syndicate.",
        906: "You don't appear to be registered as a JCR member.",
        907: "You can't do that because the ballot is in progress.",
        908: "We're not ready to do that - maybe syndicates aren't complete?"
    }
    return render(request, 'roomballot/error.html', {'message': messages[code]})


# ============== ADMIN DASHBOARD ==============
# Displays dashboard allowing system management.

def admin_dashboard(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        students = Student.objects.all()
        syndicates_complete = True
        for s in Student.objects.filter(year=1, in_ballot=True):
            if not s.accepted_syndicate:
                syndicates_complete = False
        randomised = True if settings['randomised'] == 'true' else False
        in_progress = True if settings['ballot_in_progress'] == 'true' else False
        return render(request, 'roomballot/dashboard-admin.html', {'students': students,
                                                                   'syndicates_complete': syndicates_complete,
                                                                   'randomised': randomised,
                                                                   'in_progress': in_progress,
                                                                   'syndicates': Syndicate.objects.all()})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============== BALLOT RANKING ===============
# Displays students ranked by ballot order.

def ballot_ranking(request):
    Student.objects.get(user_id=request.user.username)
    ranked_students = Student.objects.filter(in_ballot=True).order_by('rank')
    return render(request, 'roomballot/ranking.html', {'students': ranked_students})


# ============== STUDENT DETAIL ===============
# Displays student metadata.

def student_detail(request, user_id):
    student = get_object_or_404(Student, user_id=user_id)
    room = Room.objects.get(taken_by=student) if student.has_allocated else None
    return render(request, 'roomballot/student-detail.html', {'student': student,
                                                              'room': room})


# ============== MANAGE STUDENT ===============
# Allows registered admins to perform operations
# on given student.

def manage_student(request, user_id):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        student = get_object_or_404(Student, user_id=user_id)
        if request.method == 'POST':
            response_code = 900
            # Clicked 'Remove from Ballot'.
            if request.POST.get('response') == '1':
                try:
                    remove_from_ballot(student)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905
                except BallotInProgressException:
                    response_code = 907

            # Clicked 'Deallocate Room'.
            elif request.POST.get('response') == '2':
                try:
                    deallocate_room(student)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905

            # Selected a room to allocate.
            elif request.POST.get('response') == '3':
                try:
                    room = get_object_or_404(Room, pk=request.POST.get('id'))
                    allocate_room(room, student)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905

            # Selected a syndicate to allocate.
            elif request.POST.get('response') == '4':
                try:
                    syndicate = get_object_or_404(Syndicate, pk=request.POST.get('id'))
                    readd_to_ballot(student, syndicate)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905

            # Clicked 'Add to Ballot'.
            elif request.POST.get('response') == '5':
                try:
                    student.in_ballot = True
                    student.save()
                    response_code = 1
                except BallotInProgressException:
                    response_code = 907

            # Clicked 'Accept Syndicate'
            elif request.POST.get('response') == '6':
                try:
                    accept_syndicate(student)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905

            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            room = None
            if student.has_allocated:
                room = Room.objects.get(taken_by=student)
            rooms = Room.objects.filter(taken_by=None)
            syndicates = Syndicate.objects.filter(year=student.year)
            return render(request, 'roomballot/student-manage.html', {'student': student,
                                                                      'room': room,
                                                                      'rooms': rooms,
                                                                      'syndicates': syndicates})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ================ BALLOT INFO ================
# Display page with information about ballot.

def ballot_info(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info.html', {'student': student,
                                                    'date': settings['start_date']})


# ================== STATUS ===================
# Display page with ballot status - which students
# haven't completed syndicate, which syndicates are
# complete, etc.

def status(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        incomplete_students = []
        for student in Student.objects.filter(in_ballot=True).order_by('first_name'):
            if not student.accepted_syndicate or not student.syndicate.complete:
                incomplete_students.append(student)
        return render(request, 'roomballot/status.html', {'syndicates': Syndicate.objects.all(),
                                                          'incomplete_students': incomplete_students,
                                                          'students_outside_ballot': Student.objects.filter(in_ballot=False),
                                                          'incomplete_syndicates': Syndicate.objects.filter(complete=False)})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============ MANAGE SYNDICATE ===============
# Admin page to manage syndicate.

def manage_syndicate(request, syndicate_id):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        syndicate = Syndicate.objects.get(syndicate_id=syndicate_id)
        if request.method == 'POST':
            response_code = 900
            # Clicked 'Remove from Ballot'.
            if request.POST.get('response') == '1':
                dissolve_syndicate(syndicate)
                response_code = 1
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            students = Student.objects.filter(syndicate=syndicate).order_by('first_name')
            return render(request, 'roomballot/syndicate-manage.html', {'syndicate': syndicate,
                                                                        'students': students})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============= SYNDICATES LIST ===============
# Admin page listing all syndicates.

def syndicates_list(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        syndicates = Syndicate.objects.all().order_by('syndicate_id')
        return render(request, 'roomballot/syndicate-list.html', {'syndicates': syndicates})
    except AdminUser.DoesNotExist:
        return error(request, 403)