"""
VIEWS
Defines views to be used in this application.
Author Cameron O'Connor
"""

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings as django_settings
from django.db import transaction
from .models import *
from .methods import *
from .forms import *
import json
import csv
import numpy as np


# ================ ROOM DETAIL ===================
# Displays room metadata.

def room_detail(request, room_id):
    try:
        student = Student.objects.get(user_id=request.user.username)
    except Student.DoesNotExist:
        student = ProxyUser.objects.get(user_id=request.user.username)
    room = get_object_or_404(Room, pk=room_id)
    reviews = Review.objects.filter(room=room)
    selectable = get_setting('ballot_in_progress') == 'true' and get_setting('current_student') == request.user.username
    return render(request, 'roomballot/room-detail-view.html', {'room': room,
                                                                'images': Image.objects.filter(room=room),
                                                                'student': student,
                                                                'reviews': reviews,
                                                                'selectable': selectable})


# =============== ROOM PRICING ===================
# Displays room pricing methodology.

def room_pricing(request, room_id):
    try:
        student = Student.objects.get(user_id=request.user.username)
    except Student.DoesNotExist:
        student = ProxyUser.objects.get(user_id=request.user.username)
    room = get_object_or_404(Room, pk=room_id)
    y = round(float(get_setting('feature_price')), 5)
    base_price = round(float(get_setting('base_price')), 2)
    return render(request, 'roomballot/room-detail-pricing.html', {'room': room,
                                                                   'student': student,
                                                                   'y': y,
                                                                   'base_price': base_price})


# =========== ROOM SELECTION CONFIRM ==============
# Prompts user to confirm that they have selected the
# correct room.

def room_selection_confirm(request, room_id):
    student = Student.objects.get(user_id=request.user.username)
    room = get_object_or_404(Room, pk=room_id)
    can_allocate = get_setting('ballot_in_progress') == 'true' and get_setting(
        'current_student') == request.user.username and room.type == 2
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
    try:
        student = Student.objects.get(user_id=request.user.username)
    except Student.DoesNotExist:
        student = ProxyUser.objects.get(user_id=request.user.username)
    staircases = Staircase.objects.order_by('name')

    # Getting metadata

    class ModifiedStaircase(object):
        pass

    modified_staircases = []
    for staircase in staircases:
        rooms = Room.objects.filter(staircase=staircase).exclude(type=4).exclude(type=1)
        total_rooms = rooms.count()
        if total_rooms == 0:
            continue
        available_rooms_qset = rooms.filter(type=2, taken_by=None)
        available_rooms = available_rooms_qset.count()
        ensuite = available_rooms_qset.filter(is_ensuite=True).count()
        double = available_rooms_qset.filter(is_double_bed=True).count()
        ms = ModifiedStaircase()
        ms.name = staircase.name
        ms.total_rooms = total_rooms
        ms.available_rooms = available_rooms
        ms.double_rooms = double
        ms.ensuite_rooms = ensuite
        ms.staircase_id = staircase.staircase_id
        modified_staircases.append(ms)
    return render(request, 'roomballot/staircase-list.html', {'staircases': modified_staircases,
                                                              'student': student})


# ============= STAIRCASE DETAIL =================
# Shows staircase metadata, and all rooms on this
# given staircase.

def staircase_detail(request, staircase_id):
    try:
        student = Student.objects.get(user_id=request.user.username)
    except Student.DoesNotExist:
        student = ProxyUser.objects.get(user_id=request.user.username)
    staircase = get_object_or_404(Staircase, pk=staircase_id)
    rooms = Room.objects.filter(staircase=staircase).order_by('sort_number')
    try:
        floorplan = Floorplan.objects.get(staircase=staircase)
    except:
        floorplan = None
    return render(request, 'roomballot/staircase-view.html', {'staircase': staircase,
                                                              'rooms': rooms,
                                                              'floorplan': floorplan,
                                                              'student': student})


# ============ STUDENT DASHBOARD =================
# Account dashboard for student. Displays current
# room selection status, syndicate status etc.

def student_dashboard(request):
    student = Student.objects.get(user_id=request.user.username)
    room = Room.objects.get(taken_by=student) if student.has_allocated else None
    reviews_left = Review.objects.filter(author_id=student.user_id, room=room)
    can_leave_review = reviews_left.count() == 0
    can_pick = get_setting('current_student') == request.user.username and get_setting('ballot_in_progress') == 'true'
    return render(request, 'roomballot/dashboard-student.html', {'student': student,
                                                                 'room': room,
                                                                 'can_pick': can_pick,
                                                                 'can_leave_review': can_leave_review})


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


# ============= SYNDICATE VIEW =================
# Shows syndicate information, including allowing
# user to accept if required.

def syndicate_view(request):
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


# ============ SYNDICATE DETAIL ================
# Shows detail of syndicate which student is part
# of (from ranking page)

def syndicate_detail(request, syndicate_id):
    student = Student.objects.get(user_id=request.user.username)
    syndicate = get_object_or_404(Syndicate, syndicate_id=syndicate_id)
    students = Student.objects.filter(syndicate=syndicate).order_by('surname')
    return render(request, 'roomballot/syndicate-detail.html', {'student': student,
                                                                'syndicate': syndicate,
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
        908: "We're not ready to do that - maybe syndicates aren't complete?",
        909: "Oops, there's something wrong with your review. Please try again."
    }
    return render(request, 'roomballot/error.html', {'message': messages[code]})


# ============== ADMIN DASHBOARD ==============
# Displays dashboard allowing system management.

def admin_dashboard(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        students = Student.objects.order_by('surname')
        syndicates_complete = True
        for s in Student.objects.filter(year=1, in_ballot=True):
            if not s.accepted_syndicate:
                syndicates_complete = False
        randomised = get_setting('randomised') == 'true'
        in_progress = get_setting('ballot_in_progress') == 'true'
        return render(request, 'roomballot/dashboard-admin.html', {'students': students,
                                                                   'syndicates_complete': syndicates_complete,
                                                                   'randomised': randomised,
                                                                   'in_progress': in_progress,
                                                                   'syndicates': Syndicate.objects.order_by(
                                                                       'syndicate_id'),
                                                                   'rooms': Room.objects.order_by('sort_number')})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============== BALLOT RANKING ===============
# Displays students ranked by ballot order.

def ballot_ranking(request):
    student = Student.objects.get(user_id=request.user.username)
    ranked_students = Student.objects.filter(in_ballot=True).exclude(rank=None).order_by('rank')
    return render(request, 'roomballot/ranking.html', {'student': student,
                                                       'students': ranked_students})


# ============== STUDENT DETAIL ===============
# Displays student metadata.

def student_detail(request, user_id):
    student = Student.objects.get(user_id=request.user.username)
    student_to_view = get_object_or_404(Student, user_id=user_id)
    room = Room.objects.get(taken_by=student_to_view) if student_to_view.has_allocated else None
    return render(request, 'roomballot/student-detail.html', {'student': student,
                                                              'student_to_view': student_to_view,
                                                              'room': room})


# ============== MANAGE STUDENT ===============
# Allows registered admins to perform operations
# on given student.

def manage_student(request, user_id):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        student = get_object_or_404(Student, user_id=user_id)
        in_progress = get_setting('ballot_in_progress') == 'true'
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
                    add_to_syndicate(student, syndicate)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905

            # Clicked 'Add to Ballot'.
            elif request.POST.get('response') == '5':
                try:
                    with transaction.atomic():
                        student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
                        student_to_update.in_ballot = True
                        student_to_update.save()
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
            elif request.POST.get('response') == '7':
                try:
                    send_to_bottom(student)
                    response_code = 1
                except ConcurrencyException:
                    response_code = 905
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            room = None
            if student.has_allocated:
                room = Room.objects.get(taken_by=student)
            rooms = Room.objects.filter(taken_by=None).order_by('sort_number')
            syndicates = Syndicate.objects.filter(year=student.year).order_by('syndicate_id')
            return render(request, 'roomballot/student-manage.html', {'student': student,
                                                                      'room': room,
                                                                      'rooms': rooms,
                                                                      'syndicates': syndicates,
                                                                      'in_progress': in_progress})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ================ BALLOT INFO ================
# Display page with information about ballot.

def ballot_info(request):
    student = Student.objects.get(user_id=request.user.username)
    start_date = get_setting('start_date')
    start = datetime.datetime.strptime(start_date, "%d/%m/%y")
    syndicate_end = start - datetime.timedelta(weeks=1)
    return render(request, 'roomballot/info.html', {'student': student,
                                                    'date': start.strftime("%d/%m"),
                                                    'syndicate_date': syndicate_end.strftime("%d/%m")})


# =================== ABOUT ===================
# Display page with information about this system.

def about(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/about.html', {'student': student})


# =============== SYNDICATE INFO ==============
# Display page with instructions on how to create
# a syndicate.

def syndicate_info(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info-create-syndicate.html', {'student': student})


# =============== INDIVIDUAL INFO ==============
# Display page with instructions on how to enter the
# ballot as an individual.

def individual_info(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info-individual.html', {'student': student})


# ================= BURSARY INFO ===============
# Display page with instructions on how to enter the
# ballot as an individual.

def bursary_info(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info-bursary.html', {'student': student})


# ============== SELECT ROOM INFO ==============
# Display page with instructions on how to select
# a room come ballot day.

def select_room_info(request):
    student = Student.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info-select-room.html', {'student': student})


# ================ PRICING INFO ================
# Display page with information about pricing
# policy.

def pricing_info(request):
    try:
        student = Student.objects.get(user_id=request.user.username)
    except Student.DoesNotExist:
        student = ProxyUser.objects.get(user_id=request.user.username)
    return render(request, 'roomballot/info-pricing.html', {'student': student,
                                                            'base_price': get_setting('base_price'),
                                                            'weight_ensuite': get_setting('weight_ensuite'),
                                                            'weight_bathroom': get_setting('weight_bathroom'),
                                                            'weight_double_bed': get_setting('weight_double_bed'),
                                                            'weight_size': get_setting('weight_size'),
                                                            'weight_renovated_room': get_setting(
                                                                'weight_renovated_room'),
                                                            'weight_renovated_facilities': get_setting(
                                                                'weight_renovated_facilities'),
                                                            'weight_flat': get_setting('weight_flat'),
                                                            'weight_facing_lensfield': get_setting(
                                                                'weight_facing_lensfield'),
                                                            'weight_facing_court': get_setting('weight_facing_court'),
                                                            'weight_ground_floor': get_setting('weight_ground_floor'),
                                                            'feature_multiplier': round(
                                                                float(get_setting('feature_price')), 5),
                                                            'bands': Band.objects.order_by('-weekly_price')})


# =================== PROXY ====================
# Allow selection of room by registered proxy.

def proxy(request):
    try:
        student = Student.objects.get(user_id=request.user.username)
        if request.method == 'POST':
            try:
                if ProxyInstance.objects.filter(user_id=request.POST.get('student_id'),
                                                proxy_user_id=request.user.username).count() > 0:
                    room = get_object_or_404(Room, pk=request.POST.get('room_id'))
                    allocate_room(room, Student.objects.get(user_id=request.POST.get('student_id')))
                    response_code = 1
                else:
                    response_code = 905
            except ConcurrencyException:
                response_code = 905
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            student_crsids = ProxyInstance.objects.filter(proxy_user_id=student.user_id)
            students = []
            rooms_allocated = []
            for s in student_crsids:
                st = Student.objects.get(user_id=s.user_id)
                if st.has_allocated:
                    rooms_allocated.append(Room.objects.get(taken_by=st))
                students.append(st)
            student_to_pick = None
            if get_setting('ballot_in_progress') == 'true':
                for s in students:
                    if s.user_id == get_setting('current_student'):
                        student_to_pick = s
                        break
            return render(request, 'roomballot/proxy.html', {'students': students,
                                                             'student': student,
                                                             'student_to_pick': student_to_pick,
                                                             'proxy_user': student,
                                                             'rooms': Room.objects.filter(taken_by=None).order_by(
                                                                 'sort_number'),
                                                             'rooms_allocated': rooms_allocated})
    except Student.DoesNotExist:
        try:
            proxy_user = ProxyUser.objects.get(user_id=request.user.username)
            if request.method == 'POST':
                try:
                    if ProxyInstance.objects.filter(user_id=request.POST.get('student_id'),
                                                    proxy_user_id=request.user.username).count() > 0:
                        room = get_object_or_404(Room, pk=request.POST.get('room_id'))
                        allocate_room(room, Student.objects.get(user_id=request.POST.get('student_id')))
                        response_code = 1
                    else:
                        response_code = 905
                except ConcurrencyException:
                    response_code = 905
                return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
            else:
                student_crsids = ProxyInstance.objects.filter(proxy_user_id=proxy_user.user_id)
                students = []
                rooms_allocated = []
                for s in student_crsids:
                    st = Student.objects.get(user_id=s.user_id)
                    if st.has_allocated:
                        rooms_allocated.append(Room.objects.get(taken_by=st))
                    students.append(st)
                student_to_pick = None
                if get_setting('ballot_in_progress') == 'true':
                    for s in students:
                        if s.user_id == get_setting('current_student'):
                            student_to_pick = s
                            break
                return render(request, 'roomballot/proxy.html', {'students': students,
                                                                 'student_to_pick': student_to_pick,
                                                                 'student': proxy_user,
                                                                 'proxy_user': proxy_user,
                                                                 'rooms': Room.objects.filter(taken_by=None).order_by(
                                                                     'sort_number'),
                                                                 'rooms_allocated': rooms_allocated})
        except ProxyUser.DoesNotExist:
            return error(request, 403)


# ================== STATUS ===================
# Display page with ballot status - which students
# haven't completed syndicate, which syndicates are
# complete, etc.

def status(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        randomised = get_setting('randomised') == 'true'
        in_progress = get_setting('ballot_in_progress') == 'true'
        current_student_crsid = get_setting('current_student')
        if current_student_crsid != None:
            current_student = Student.objects.get(user_id=current_student_crsid)
        else:
            current_student = None
        syndicates_complete = True
        for s in Student.objects.filter(year=1, in_ballot=True):
            if not s.accepted_syndicate:
                syndicates_complete = False
        incomplete_students = []
        for student in Student.objects.filter(in_ballot=True).order_by('first_name'):
            if not student.accepted_syndicate or not student.syndicate.complete:
                incomplete_students.append(student)
        return render(request, 'roomballot/status.html', {'syndicates': Syndicate.objects.all(),
                                                          'syndicates_complete': syndicates_complete,
                                                          'randomised': randomised,
                                                          'in_progress': in_progress,
                                                          'incomplete_students': incomplete_students,
                                                          'students_outside_ballot': Student.objects.filter(
                                                              in_ballot=False),
                                                          'incomplete_syndicates': Syndicate.objects.filter(
                                                              complete=False),
                                                          'current_student': current_student})
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
                try:
                    dissolve_syndicate(syndicate)
                    response_code = 1
                except BallotInProgressException:
                    response_code = 907
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        else:
            students = Student.objects.filter(syndicate=syndicate).order_by('first_name')
            in_progress = get_setting('ballot_in_progress') == 'true'
            return render(request, 'roomballot/syndicate-manage.html', {'syndicate': syndicate,
                                                                        'students': students,
                                                                        'in_progress': in_progress})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ========= CREATE SYNDICATE ADMIN ============
# Allows admin user to create a new syndicate.

def create_syndicate_admin(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        if request.method == 'POST':
            usernames = request.POST.getlist('crsids[]')
            syndicate_id = 0
            try:
                syndicate_id = create_new_syndicate(usernames, usernames[0])
                response_code = 1
            except ConcurrencyException:
                response_code = 901
            except BallotInProgressException:
                response_code = 907
            return HttpResponse(json.dumps({'responseCode': response_code, 'newSyndicateId': syndicate_id}),
                                content_type="application/json")
        else:
            return render(request, 'roomballot/create-syndicate-admin.html',
                          {'students': Student.objects.filter(syndicate=None,
                                                              in_ballot=True)})
    except AdminUser.DoesNotExist:
        return error(request, 403)
    except BallotInProgressException:
        return error(request, 907)


# ============= SYNDICATES LIST ===============
# Admin page listing all syndicates.

def syndicates_list(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        syndicates = Syndicate.objects.all().order_by('syndicate_id')
        return render(request, 'roomballot/syndicate-list.html', {'syndicates': syndicates})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============== STUDENTS LIST ================
# Admin page listing all students.

def students_list(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        students = Student.objects.order_by('year', 'surname')
        return render(request, 'roomballot/student-list.html', {'students': students})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ================ ROOMS LIST =================
# Admin page listing all rooms.

def rooms_list(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        rooms = Room.objects.order_by('new_price')  # 'staircase', 'sort_number') # TODO: change this back
        return render(request, 'roomballot/rooms-list.html', {'rooms': rooms})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# =============== MANAGE ROOM =================
# Admin page showing room detail.

def manage_room(request, room_id):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        if request.method == 'POST':
            response_code = 900
            # Clicked 'JCR Freshers'.
            if request.POST.get('response') == '1':
                if get_setting('ballot_in_progress') != 'true':
                    with transaction.atomic():
                        room = Room.objects.select_for_update().get(room_id=room_id)
                        room.type = 1
                        response_code = 1
                        room.save()
            if request.POST.get('response') == '2':
                if get_setting('ballot_in_progress') != 'true':
                    with transaction.atomic():
                        room = Room.objects.select_for_update().get(room_id=room_id)
                        room.type = 2
                        response_code = 1
                        room.save()
            if request.POST.get('response') == '3':
                if get_setting('ballot_in_progress') != 'true':
                    with transaction.atomic():
                        room = Room.objects.select_for_update().get(room_id=room_id)
                        room.type = 3
                        response_code = 1
                        room.save()
            if request.POST.get('response') == '4':
                if get_setting('ballot_in_progress') != 'true':
                    with transaction.atomic():
                        room = Room.objects.select_for_update().get(room_id=room_id)
                        room.type = 4
                        response_code = 1
                        room.save()
            return HttpResponse(json.dumps({'responseCode': response_code}), content_type="application/json")
        in_progress = get_setting('ballot_in_progress') == 'true'
        room = get_object_or_404(Room, room_id=room_id)
        return render(request, 'roomballot/room-manage.html', {'room': room,
                                                               'in_progress': in_progress})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# =============== EXPORT DATA =================
# Admin views to export data in CSV format.

def export_student_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Surname', 'CRSid', 'Room'])
    for s in Student.objects.order_by('surname'):
        try:
            room = Room.objects.get(taken_by=s)
        except Room.DoesNotExist:
            room = None
        writer.writerow([s.first_name, s.surname, s.user_id, room])
    return response


def export_room_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Room ID', 'Staircase', 'Number', 'Type', 'Old Band', 'New Band', 'Continuous Price', 'Occupant', 'CRSid'])
    for r in Room.objects.order_by('staircase', 'sort_number'):
        writer.writerow([r.room_id, r.staircase, r.room_number, r.get_type_display(), r.band.band_name, r.new_band.band_name, r.new_price, r.taken_by,
                         r.taken_by.user_id if r.taken_by else None])
    return response


# ============== LEAVE REVIEW =================
# Allows user to leave a review of their room.

def leave_review(request):
    student = Student.objects.get(user_id=request.user.username)
    if student.has_allocated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                room = Room.objects.get(taken_by=student)
                with transaction.atomic():
                    review = Review()
                    review.room = room
                    review.author_name = str(student)
                    review.author_id = student.user_id
                    review.title = form.cleaned_data['title']
                    review.layout_rating = form.cleaned_data['layout_rating']
                    review.facilities_rating = form.cleaned_data['facilities_rating']
                    review.noise_rating = form.cleaned_data['noise_rating']
                    review.overall_rating = form.cleaned_data['overall_rating']
                    review.text = form.cleaned_data['text']
                    review.save()
                confirm_review(student)
                return render(request, 'roomballot/create-review-success.html', {'student': student})
            else:
                return error(request, 909)
        else:
            room = Room.objects.get(taken_by=student)
            reviews_left = Review.objects.filter(author_id=student.user_id, room=room)
            if reviews_left.count() != 0:
                return error(request, 404)
            images = Image.objects.filter(room=room)
            if images.count() != 0:
                image = images[0]
            else:
                image = None
            return render(request, 'roomballot/create-review.html', {'student': student,
                                                                     'room': room,
                                                                     'image': image})
    else:
        return error(request, 404)


# ============= SET FIRST NAME ================
# Invites user to set their name.

def set_first_name(request):
    if request.method == 'POST':
        form = FirstNameForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                s = Student.objects.select_for_update().get(user_id=request.user.username)
                s.first_name = form.cleaned_data['first_name']
                s.name_set = True
                s.save()
            return HttpResponseRedirect('/roomballot/dashboard')
    else:
        student = Student.objects.get(user_id=request.user.username)
        return render(request, 'roomballot/enter-name.html', {'student': student})


# ============ RANKING (ADMIN) ================
# Page for admin portal showing admin ranking.

def ranking_admin(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        students = Student.objects.filter(in_ballot=True).order_by('rank')
        return render(request, 'roomballot/ranking-admin.html', {'students': students})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# =============== ANALYTICS ===================
# Admin page with some useful analytics information.

def analytics(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)

        class BandCount(object):
            pass

        jcr_rooms = Room.objects.exclude(type=4)
        jcr_rooms_count = jcr_rooms.count()
        total_rooms_count = Room.objects.all().count()
        contract_weeks = 0

        # Calculating the number of rooms in each band.
        band_counts = []
        for b in Band.objects.all():
            bc = BandCount()
            bc.band_name = b.band_name
            bc.count = Room.objects.filter(new_band=b).count()
            bc.percentage = round(bc.count / total_rooms_count * 100, 1)
            bc.total_jcr = jcr_rooms.filter(new_band=b).count()
            band_counts.append(bc)

        band_counts_old = []
        for b in Band.objects.exclude(weekly_price_old=None):
            bc = BandCount()
            bc.band_name = b.band_name
            bc.count = Room.objects.filter(band=b).count()
            bc.percentage = round(bc.count / total_rooms_count * 100, 1)
            bc.total_jcr = jcr_rooms.filter(band=b).count()
            band_counts_old.append(bc)

        jcr_x_values = np.arange(jcr_rooms_count)
        jcr_x_values += 1
        jcr_prices = []
        jcr_new_prices = []
        jcr_total_prices = []
        jcr_total_new_prices = []
        for r in jcr_rooms.order_by('-new_band'):
            jcr_prices.append(r.band.weekly_price)
            jcr_new_prices.append(r.new_band.weekly_price)
            if r.contract_length == 37 and not r.identifier.__contains__("BL"):
                jcr_total_prices.append(r.band.weekly_price_old * 35)
                jcr_total_new_prices.append(r.new_band.weekly_price * 35)
                contract_weeks += 35
            else:
                jcr_total_prices.append(r.band.weekly_price_old * r.contract_length)
                jcr_total_new_prices.append(r.new_band.weekly_price * r.contract_length)
                contract_weeks += r.contract_length
        jcr_prices = np.array(jcr_prices)
        jcr_total_prices = np.array(jcr_total_prices)
        jcr_new_prices = np.array(jcr_new_prices)
        jcr_total_new_prices = np.array(jcr_total_new_prices)

        total = np.sum(jcr_total_prices)
        new_total = np.sum(jcr_total_new_prices)

        average_weekly_price_jcr = np.mean(jcr_new_prices)
        median_weekly_price_jcr = np.median(jcr_new_prices)
        jcr_range = (np.max(jcr_new_prices) - np.min(jcr_new_prices)) if jcr_rooms_count > 0 else 0
        jcr_std = np.std(jcr_new_prices)

        jcr_coeffs = np.polyfit(jcr_x_values, jcr_new_prices, 5) if jcr_rooms_count > 0 else np.array([0])
        jcr_fitted = np.poly1d(jcr_coeffs)(jcr_x_values)

        return render(request, 'roomballot/analytics.html', {'band_counts': band_counts,
                                                             'band_counts_old': band_counts_old,
                                                             'average_weekly_price_jcr': average_weekly_price_jcr,
                                                             'jcr_prices': jcr_new_prices,
                                                             'jcr_rooms_count': jcr_rooms_count,
                                                             'median_weekly_price_jcr': median_weekly_price_jcr,
                                                             'jcr_range': jcr_range,
                                                             'jcr_std': jcr_std,
                                                             'jcr_fitted': jcr_fitted,
                                                             'total': total,
                                                             'new_total': new_total,
                                                             'contract_weeks': contract_weeks})
    except AdminUser.DoesNotExist:
        return error(request, 403)


# ============= CHANGE WEIGHTS ================
# Admin page allowing easy changing of accommodation
# pricing weight changes.

def change_weights(request):
    try:
        AdminUser.objects.get(user_id=request.user.username)
        if request.method == 'POST':
            form = WeightsForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    set_setting('base_price', form.cleaned_data['base_price'])
                    set_setting('weight_ensuite', form.cleaned_data['weight_ensuite'])
                    set_setting('weight_bathroom', form.cleaned_data['weight_bathroom'])
                    set_setting('weight_double_bed', form.cleaned_data['weight_double_bed'])
                    set_setting('weight_size', form.cleaned_data['weight_size'])
                    set_setting('weight_renovated_room', form.cleaned_data['weight_renovated_room'])
                    set_setting('weight_renovated_facilities', form.cleaned_data['weight_renovated_facilities'])
                    set_setting('weight_flat', form.cleaned_data['weight_flat'])
                    set_setting('weight_facing_lensfield', form.cleaned_data['weight_facing_lensfield'])
                    set_setting('weight_facing_court', form.cleaned_data['weight_facing_court'])
                    set_setting('weight_ground_floor', form.cleaned_data['weight_ground_floor'])
                    set_setting('total', form.cleaned_data['total'])
                return HttpResponseRedirect('/roomballot/admin/change-weights')
            elif request.POST.get('response') == '1':
                generate_price()
                return HttpResponse(json.dumps({'responseCode': 1}), content_type="application/json")
        else:
            in_progress = get_setting('ballot_in_progress') == 'true'
            return render(request, 'roomballot/change-weights.html',
                          {'base_price': get_setting('base_price'),
                           'weight_ensuite': get_setting('weight_ensuite'),
                           'weight_bathroom': get_setting('weight_bathroom'),
                           'weight_double_bed': get_setting('weight_double_bed'),
                           'weight_size': get_setting('weight_size'),
                           'weight_renovated_room': get_setting('weight_renovated_room'),
                           'weight_renovated_facilities': get_setting('weight_renovated_facilities'),
                           'weight_flat': get_setting('weight_flat'),
                           'weight_facing_lensfield': get_setting('weight_facing_lensfield'),
                           'weight_facing_court': get_setting('weight_facing_court'),
                           'weight_ground_floor': get_setting('weight_ground_floor'),
                           'total': get_setting('total'),
                           'in_progress': in_progress})
    except AdminUser.DoesNotExist:
        return error(request, 403)
