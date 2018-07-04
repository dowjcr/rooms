"""
METHODS
Defines helper methods which are relied on for function.
"""


from .models import *
from .email import *
import random


class ConcurrencyException(Exception):
    pass


# ============== ALLOCATE ROOM ===================
# Takes a room and student, and tries to allocate that
# room to that student. If room has already been allocated,
# or student already has a room, then raises exception.

def allocate_room(room, student):
    if student.has_allocated or room.taken_by is not None or student.syndicate is None \
            or not student.accepted_syndicate or not student.syndicate.complete:
        raise ConcurrencyException()
    else:
        room.taken_by = student
        room.save()
        student.has_allocated = True
        student.save()
        #selected_room(student)


# ============= DEALLOCATE ROOM ==================
# Takes a room and tries to deallocate it. Raises
# exception if no student has been allocated to it.

def deallocate_room(room):
    if room.taken_by is None:
        raise Exception()   # TODO: handle this error.
    else:
        student = room.taken_by
        student.has_allocated = False
        student.save()
        room.taken_by = None
        room.save()


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
    return qset.len()


def get_num_first_year_syndicates():
    qset = Syndicate.objects.filter(year=1)
    return qset.len()


# ========== SECOND YEARS IN BALLOT ==============
# Methods to get the number of second-years who are
# taking part in the ballot, and the number of
# second-year syndicates.

def get_num_second_years_in_ballot():
    qset = Student.objects.filter(year=2, in_ballot=True)
    return qset.len()


def get_num_second_year_syndicates():
    qset = Syndicate.objects.filter(year=2)
    return qset.len()


# =============== SYNDICATE SIZE =================
# Takes a syndicate, and returns the number of
# students who are part of that syndicate.

def get_syndicate_size(syndicate):
    qset = Student.objects.filter(syndicate=syndicate)
    return qset.len()

def get_num_syndicates():
    qset = Syndicate.objects.all()
    return qset.len()


# ============= RANDOMISE ORDER ==================
# Randomises the syndicate order for first-years,
# then the order within the syndicates, and updates
# order attribute for each student.
# Has been optimised to reduce database redundancy,
# rather than to run efficiently.

def randomise_order():
    syndicates = []
    for s in Syndicate.objects.filter(year=1):
        syndicates.append(s)
    random.shuffle(syndicates)
    current_rank_student = 1 + get_num_second_years_in_ballot()
    current_rank_syndicate = 1 + get_num_second_year_syndicates()
    for syndicate in syndicates:
        students = []
        for student in Student.objects.filter(syndicate=syndicate):
            student.append(student)
            random.shuffle(students)
        for student in students:
            student.rank = current_rank_student
            student.save()
            current_rank_student += 1
        syndicate.rank = current_rank_syndicate
        syndicate.save()
        current_rank_syndicate += 1


# =============== ADVANCE YEAR ===================
# Converts first-years to second-years, and updates
# ranking to be reverse of that previously. Clears
# ranking of previous second-years, but doesn't
# delete them from Student table.

def advance_year():
    # First clear data pertaining to current second-years.
    second_year_students = Student.objects.filter(year=2)
    for student in second_year_students:
        student.syndicate = None
        student.rank = None
        student.year = None
        student.save()
    second_year_syndicates = Syndicate.objects.filter(year=2)
    for syndicate in second_year_syndicates:
        syndicate.year = None
        syndicate.save()
    # Now convert rankings and update year attributes.
    ranked_first_year_students = Student.objects.filter(year=1, in_ballot=True).order_by('-rank')
    current_rank_student = 1
    for student in ranked_first_year_students:
        student.rank = current_rank_student
        student.year = 2
        current_rank_student += 1
        student.save()
    ranked_first_year_syndicates = Syndicate.objects.filter(year=1).order_by('-rank')
    current_rank_syndicate = 1
    for syndicate in ranked_first_year_syndicates:
        syndicate.rank = current_rank_syndicate
        syndicate.year = 2
        current_rank_syndicate += 1
        syndicate.save()


# ============ REMOVE FROM BALLOT ================
# Takes a student and removes them from the ballot,
# by removing them from rankings and their syndicate.

def remove_from_ballot(student):
    # TODO: don't allow this if the ballot has already started!
    student_rank = student.rank
    student_syndicate = student.syndicate
    student.rank = None
    student.syndicate = None
    student.in_ballot = False
    student.save()
    number_in_ballot = get_num_first_years_in_ballot() + get_num_second_years_in_ballot()
    # Now decrease rank of all subsequent students.
    for rank in range(student_rank+1, number_in_ballot+1):
        st = Student.objects.get(rank=rank)
        st.rank -= 1
        st.save()
    # If syndicate is now empty, delete it and update ranks.
    if get_syndicate_size(student_syndicate) == 0:
        syndicate_rank = student_syndicate.rank
        student_syndicate.delete()
        for rank in range(syndicate_rank+1, get_num_syndicates()+2):
            sy = Syndicate.objects.get(rank=rank)
            sy.rank -= 1
            sy.save()


# ============= RE-ADD TO BALLOT =================
# Re-adds a student who has been removed from the
# ballot. A pre-existing syndicate MUST be specified,
# then the student will be added last in the syndicate.

def readd_to_ballot(student, syndicate):
    # TODO: don't allow this if the ballot has already started!
    syndicate_rank = syndicate.rank
    # Increments the student rank of all students in subsequent syndicates.
    new_rank = 1 + get_num_first_years_in_ballot() + get_num_second_years_in_ballot()
    for rank in range(syndicate_rank+1, get_num_syndicates()+1):
        sy = Syndicate.objects.get(rank=rank)
        for st in Student.objects.filter(syndicate=sy):
            new_rank = min(new_rank, st.rank)
            st.rank += 1
            st.save()
    student.in_ballot = True
    student.syndicate = syndicate
    student.rank = new_rank
    student.save()


# ============= CREATE SYNDICATE =================
# Creates a new syndicate, and sends invitations
# to the concerned students.

def create_new_syndicate(student_ids, owner_id):
    owner = Student.objects.get(user_id=owner_id)
    size = len(student_ids)
    if owner.syndicate is not None or owner.accepted_syndicate or size > 6 or size < 1:
        raise ConcurrencyException()
    else:
        syndicate = Syndicate()
        syndicate.year = 1
        syndicate.owner_id = owner_id
        if len(student_ids) == 1:
            syndicate.complete = True
        syndicate.save()
        for student_id in student_ids:
            student = Student.objects.get(user_id=student_id)
            if student.syndicate is not None or student.accepted_syndicate:
                # If we get to a student who already has a syndicate
                dissolve_syndicate(syndicate)
                raise ConcurrencyException()
            else:
                student.syndicate = syndicate
                student.accepted_syndicate = False
                student.save()
        owner = Student.objects.get(user_id=owner_id)
        owner.accepted_syndicate = True
        owner.save()
        #invite_syndicate(syndicate)


# ============ DISSOLVE SYNDICATE ================
# Takes a syndicate and dissolves it, updating the
# students' attributes.

def dissolve_syndicate(syndicate):
    # TODO: don't allow this if the syndicates have already been randomised!
    for student in Student.objects.filter(syndicate=syndicate):
        student.syndicate = None
        student.accepted_syndicate = False
        student.save()
    syndicate.delete()


# ============= ACCEPT SYNDICATE =================
# Takes a user and updates to show they have accepted
# the syndicate. Sends an email to all users if
# syndicate is now complete.

def accept_syndicate(student):
    if student.accepted_syndicate:
        print("oops")
        raise ConcurrencyException()
    else:
        student.accepted_syndicate = True
        student.save()
        syndicate = student.syndicate
        accepted = True
        for student in Student.objects.filter(syndicate=syndicate):
            if not student.accepted_syndicate:
                accepted = False
        if accepted:
            syndicate.complete = True
            syndicate.save()
            #completed_syndicate(syndicate)


# ============= DECLINE SYNDICATE =================
# Takes a user and dissolves the syndicate, sending
# an explanatory email to all members.

def decline_syndicate(student):
    if student.accepted_syndicate:
        raise Exception()   # TODO: handle this error (already accepted).
    else:
        syndicate = student.syndicate
        for student in Student.objects.filter(syndicate=syndicate):
            student.syndicate = None
            student.accepted_syndicate = False
            student.save()
        # failed_syndicate(syndicate)
        syndicate.delete()