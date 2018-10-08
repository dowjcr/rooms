"""
METHODS
Defines helper methods which are relied on for function.
Author Cameron O'Connor
"""

from .models import *
from .email import *
import random, datetime
from modeldict import ModelDict
from django.db import transaction

settings = ModelDict(Setting, key='key', value='value', instances=False)


class ConcurrencyException(Exception):
    pass

class BallotInProgressException(Exception):
    pass

class NotReadyToRandomiseException(Exception):
    pass


# ============== ALLOCATE ROOM ===================
# Takes a room and student, and tries to allocate that
# room to that student. If room has already been allocated,
# or student already has a room, then raises exception.

def allocate_room(room, student):
    if student.has_allocated or room.taken_by is not None:
        raise ConcurrencyException()
    else:
        with transaction.atomic():
            room_to_update = Room.objects.select_for_update().get(room_id=room.room_id)
            room_to_update.taken_by = student
            room_to_update.save()
        with transaction.atomic():
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_to_update.has_allocated = True
            student_to_update.save()
        #selected_room(student)


# ============= DEALLOCATE ROOM ==================
# Takes a student and tries to deallocate their room.
# Raises exception if no room allocated.

def deallocate_room(student):
    if not student.has_allocated:
        raise ConcurrencyException()
    else:
        with transaction.atomic():
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_to_update.has_allocated = False
            student_to_update.save()
        with transaction.atomic():
            try:
                room_to_update = Room.objects.select_for_update().get(taken_by=student)
                room_to_update.taken_by = None
                room_to_update.save()
            except Room.DoesNotExist:
                raise ConcurrencyException()


# ============= GENERATE PRICE ===================
# Takes a room and generates its price.

def generate_price(room):
    # TODO: implement this.
    return 0


# ========== FIRST YEARS IN BALLOT ===============
# Methods to get the number of first-years who are taking part
# in the ballot, and the number of first-year syndicates.

def get_num_first_years_in_ballot():
    qset = Student.objects.filter(year=1, in_ballot=True)
    return qset.count()


def get_num_first_year_syndicates():
    qset = Syndicate.objects.filter(year=1)
    return qset.count()


# ========== SECOND YEARS IN BALLOT ==============
# Methods to get the number of second-years who are
# taking part in the ballot, and the number of
# second-year syndicates.

def get_num_second_years_in_ballot():
    qset = Student.objects.filter(year=2, in_ballot=True)
    return qset.count()


def get_num_second_year_syndicates():
    qset = Syndicate.objects.filter(year=2)
    return qset.count()


# =============== SYNDICATE SIZE =================
# Takes a syndicate, and returns the number of
# students who are part of that syndicate.

def get_syndicate_size(syndicate):
    qset = Student.objects.filter(syndicate=syndicate)
    return qset.count()

def get_num_syndicates():
    qset = Syndicate.objects.all()
    return qset.count()


# ============= RANDOMISE ORDER ==================
# Randomises the syndicate order for first-years,
# then the order within the syndicates, and updates
# order attribute for each student.
# Has been optimised to reduce database redundancy,
# rather than to run efficiently.

def randomise_order():
    if settings['ballot_in_progress'] == 'false':
        syndicates = []
        settings['randomised'] = False
        # First check all students either in syndicate or removed from ballot.
        for s in Student.objects.filter(year=1):
            if s.in_ballot and not s.accepted_syndicate:
                raise NotReadyToRandomiseException()
        # Now get all first-year syndicates.
        with transaction.atomic():
            for s in Syndicate.objects.select_for_update().filter(year=1):
                if not s.complete:
                    raise NotReadyToRandomiseException()
                syndicates.append(s)
            random.shuffle(syndicates)
            current_rank_student = 1 + get_num_second_years_in_ballot()
            current_rank_syndicate = 1 + get_num_second_year_syndicates()
            for syndicate in syndicates:
                students = []
                for student in Student.objects.select_for_update().filter(syndicate=syndicate):
                    students.append(student)
                    random.shuffle(students)
                for student in students:
                    student.rank = current_rank_student
                    student.save()
                    current_rank_student += 1
                syndicate.rank = current_rank_syndicate
                syndicate.save()
                current_rank_syndicate += 1
            settings['randomised'] = 'true'
        generate_times()
    else:
        raise BallotInProgressException()


# =============== ADVANCE YEAR ===================
# Converts first-years to second-years, and updates
# ranking to be reverse of that previously. Clears
# ranking of previous second-years, but doesn't
# delete them from Student table.

def advance_year():
    if settings['ballot_in_progress'] == 'false':
        with transaction.atomic():
            # First clear data pertaining to current second-years.
            second_year_students = Student.objects.select_for_update().filter(year=2)
            for student in second_year_students:
                student.syndicate = None
                student.rank = None
                student.picks_at = None
                student.year = 3
                student.save()
            second_year_syndicates = Syndicate.objects.select_for_update().filter(year=2)
            for syndicate in second_year_syndicates:
                syndicate.year = 3
                syndicate.save()
            # Now convert rankings and update year attributes.
            ranked_first_year_students = Student.objects.select_for_update().filter(year=1, in_ballot=True).order_by('-rank')
            current_rank_student = 1
            for student in ranked_first_year_students:
                student.rank = current_rank_student
                student.year = 2
                current_rank_student += 1
                student.save()
            ranked_first_year_syndicates = Syndicate.objects.select_for_update().filter(year=1).order_by('-rank')
            current_rank_syndicate = 1
            for syndicate in ranked_first_year_syndicates:
                syndicate.rank = current_rank_syndicate
                syndicate.year = 2
                current_rank_syndicate += 1
                syndicate.save()
    else:
        raise BallotInProgressException()


# ============ REMOVE FROM BALLOT ================
# Takes a student and removes them from the ballot,
# by removing them from rankings and their syndicate.

def remove_from_ballot(student):
    if settings['ballot_in_progress'] == 'false':
        with transaction.atomic():
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_rank = student_to_update.rank
            student_syndicate = student_to_update.syndicate
            student_to_update.rank = None
            student_to_update.syndicate = None
            student_to_update.accepted_syndicate = False
            student_to_update.in_ballot = False
            student_to_update.save()
            number_in_ballot = get_num_first_years_in_ballot() + get_num_second_years_in_ballot()
            # Now decrease rank of all subsequent students.
            if student_rank is not None:
                for rank in range(student_rank+1, number_in_ballot+1):
                    st = Student.objects.select_for_update().get(rank=rank)
                    st.rank -= 1
                    st.save()
            if student_syndicate is not None:
                # If syndicate is now empty, delete it and update ranks.
                if get_syndicate_size(student_syndicate) == 0:
                    syndicate_rank = student_syndicate.rank
                    student_syndicate.delete()
                    if syndicate_rank is not None:
                        for rank in range(syndicate_rank+1, get_num_syndicates()+2):
                            sy = Syndicate.objects.select_for_update().get(rank=rank)
                            sy.rank -= 1
                            sy.save()
                else:
                    if student_syndicate.owner_id == student.user_id:
                        reallocate_syndicate_owner(student_syndicate)
                    # Check if syndicate complete, and update if necessary.
                    complete = True
                    for student in Student.objects.filter(syndicate=student_syndicate):
                        if not student.accepted_syndicate:
                            complete = False
                            break
                    student_syndicate.complete = complete
                    student_syndicate.save()
    else:
        raise BallotInProgressException()


# ============= ADD TO SYNDICATE =================
# Adds a student to the given syndicate. A pre-existing
# syndicate must be specified, then the student will
# be added last in the syndicate.

def add_to_syndicate(student, syndicate):
    if settings['ballot_in_progress'] == 'false':
        with transaction.atomic():
            syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            syndicate_rank = syndicate_to_update.rank
            # Increments the student rank of all students in subsequent syndicates.
            #if syndicate_rank is not None:
            #    new_rank = 1 + get_num_first_years_in_ballot() + get_num_second_years_in_ballot()
            #    for rank in range(syndicate_rank+1, get_num_syndicates()+1):
            #        sy = Syndicate.objects.get(rank=rank)
            #        for st in Student.objects.select_for_update().filter(syndicate=sy):
            #            new_rank = min(new_rank, st.rank)
            #            st.rank += 1
            #            st.save()
            #    student_to_update.rank = new_rank
            student_to_update.syndicate = syndicate_to_update
            student_to_update.save()
            syndicate_to_update.complete = False
            syndicate_to_update.save()
    else:
        raise BallotInProgressException()


# ============= CREATE SYNDICATE =================
# Creates a new syndicate, and sends invitations
# to the concerned students.

def create_new_syndicate(student_ids, owner_id):
    if settings['ballot_in_progress'] == 'false':
        owner = Student.objects.get(user_id=owner_id)
        size = len(student_ids)
        if owner.syndicate is not None or owner.accepted_syndicate or size > 6 or size < 1:
            raise ConcurrencyException()
        else:
            with transaction.atomic():
                syndicate = Syndicate()
                syndicate.year = 1
                syndicate.owner_id = owner_id
                if len(student_ids) == 1:
                    syndicate.complete = True
                syndicate.save()
                for student_id in student_ids:
                    student = Student.objects.select_for_update().get(user_id=student_id)
                    if student.syndicate is not None or student.accepted_syndicate:
                        # If we get to a student who already has a syndicate
                        dissolve_syndicate(syndicate)
                        student.save()
                        raise ConcurrencyException()
                    else:
                        student.syndicate = syndicate
                        student.accepted_syndicate = False
                        student.save()
                owner = Student.objects.select_for_update().get(user_id=owner_id)
                owner.accepted_syndicate = True
                owner.save()
            #invite_syndicate(syndicate)
    else:
        raise BallotInProgressException()


# ============ DISSOLVE SYNDICATE ================
# Takes a syndicate and dissolves it, updating the
# students' attributes.

def dissolve_syndicate(syndicate):
    if settings['ballot_in_progress'] == 'true':
        raise BallotInProgressException()
    else:
        with transaction.atomic():
            syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
            for student in Student.objects.select_for_update().filter(syndicate=syndicate_to_update):
                student.syndicate = None
                student.accepted_syndicate = False
                student.save()
            syndicate_to_update.delete()


# ============= ACCEPT SYNDICATE =================
# Takes a user and updates to show they have accepted
# the syndicate. Sends an email to all users if
# syndicate is now complete.

def accept_syndicate(student):
    if student.accepted_syndicate:
        raise ConcurrencyException()
    else:
        with transaction.atomic():
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_to_update.accepted_syndicate = True
            student_to_update.save()
            syndicate = Syndicate.objects.select_for_update().get(syndicate_id=student_to_update.syndicate.syndicate_id)
            accepted = True
            for s in Student.objects.filter(syndicate=syndicate):
                if not s.accepted_syndicate:
                    accepted = False
            if accepted:
                syndicate.complete = True
                syndicate.save()
            else:
                syndicate.complete = False
                syndicate.save()
            #completed_syndicate(syndicate)


# ============= DECLINE SYNDICATE =================
# Takes a user and dissolves the syndicate, sending
# an explanatory email to all members.

def decline_syndicate(student):
    if student.accepted_syndicate:
        raise ConcurrencyException()
    else:
        syndicate = Syndicate.objects.select_for_update().get(syndicate_id=student.syndicate.syndicate_id)
        for student in Student.objects.filter(syndicate=syndicate):
            student.syndicate = None
            student.accepted_syndicate = False
            student.save()
        # failed_syndicate(syndicate)
        syndicate.delete()


# ======== RE-ALLOCATE SYNDICATE OWNER ============
# Takes a syndicate whose owner has just been removed
# from the ballot, and re-allocates ownership.
# Inductively, syndicate must be non-empty.

def reallocate_syndicate_owner(syndicate):
    students = Student.objects.filter(syndicate=syndicate)
    syndicate.owner_id = students[0].user_id
    syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
    syndicate_to_update.save()


# =============== GENERATE TIMES ==================
# Takes a start date, and generates the times at which
# each person is to choose their room. Second years on
# the first day, first years on the second.
# Date in datetime format.

def generate_times():
    if settings['ballot_in_progress'] == 'false':
        for s in Student.objects.select_for_update().filter(in_ballot=True):
            s.picks_at = None
            s.save()
        start_date = settings['start_date']
        # Generate times for second years.
        second_years = Student.objects.select_for_update().filter(year=2, in_ballot=True).exclude(rank=None).order_by('rank')
        dt = datetime.datetime.strptime(start_date + " 09:00", "%d/%m/%y %H:%M")
        for student in second_years:
            student.picks_at = dt
            student.save()
            dt += datetime.timedelta(0,300)

        # Generate times for first years.
        first_years = Student.objects.select_for_update().filter(year=1, in_ballot=True).exclude(rank=None).order_by('rank')
        dt = datetime.datetime.strptime(start_date + " 09:00", "%d/%m/%y %H:%M") + datetime.timedelta(1)
        for student in first_years:
            student.picks_at = dt
            student.save()
            dt += datetime.timedelta(0, 300)
    else:
        raise BallotInProgressException()


# ========== UPDATE CURRENT STUDENT ==============
# When run, gets student who should be picking
# at current time, and updates setting field.

def update_current_student():
    if settings['ballot_in_progress'] != 'true':
        raise ConcurrencyException()
    else:
        current_datetime = datetime.datetime.now()
        slot_datetime = current_datetime - datetime.timedelta(minutes=current_datetime.minute % 5,
                                                              seconds=current_datetime.second,
                                                              microseconds=current_datetime.microsecond)
        try:
            student_picking = Student.objects.get(picks_at=slot_datetime)
            settings['current_student'] = student_picking.user_id
        except Student.DoesNotExist:
            settings['current_student'] = None