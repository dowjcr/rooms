"""
METHODS
Defines helper methods which are relied on for function.
Author Cameron O'Connor
"""

from .models import *
from .email import *
import random, datetime
from django.db import transaction
from ibisclient import *

LOG_FILE = 'roomballot.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ConcurrencyException(Exception):
    pass


class BallotInProgressException(Exception):
    pass


class NotReadyToRandomiseException(Exception):
    pass


class StudentAlreadyExistsException(Exception):
    pass


class InvalidIdentifierException(Exception):
    pass


def get_setting(key):
    return Setting.objects.get(key=key).value


def set_setting(key, value):
    setting = Setting.objects.get(key=key)
    setting.value = value
    setting.save()


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
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_to_update.has_allocated = True
            student_to_update.save()
            selected_room(student, room)
            logger.info("Selected room [" + student.user_id + "] [Room" + str(room.room_id) + "]")


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
            logger.info("Deallocating room - updated student [" + student.user_id + "]")
            try:
                room_to_update = Room.objects.select_for_update().get(taken_by=student)
                room_to_update.taken_by = None
                room_to_update.save()
                logger.info("Deallocating room - updated room [" + str(room_to_update.room_id) + "]")
            except Room.DoesNotExist:
                raise ConcurrencyException()


# ============= GENERATE PRICE ===================
# Takes all rooms and generates their price.

def generate_price():
    # Counts - contain number of accommodation weeks with that feature.
    count_ensuite = 0
    count_double_bed = 0
    count_size = 0
    count_bathroom = 0
    count_renovated_room = 0
    count_renovated_facilities = 0
    count_flat = 0
    count_facing_lensfield = 0
    count_facing_court = 0
    count_ground_floor = 0

    # Useful constants.
    min_size = Room.objects.order_by('size')[0].size if Room.objects.all().count() > 0 else 0
    max_size = Room.objects.order_by('-size')[0].size if Room.objects.all().count() > 0 else 0
    min_renovated_room = Room.objects.exclude(room_last_renovated=None).order_by('room_last_renovated')[
        0].room_last_renovated if Room.objects.all().count() > 0 else 0
    max_renovated_room = Room.objects.exclude(room_last_renovated=None).order_by('-room_last_renovated')[
        0].room_last_renovated if Room.objects.all().count() > 0 else 0
    min_renovated_bathroom = Room.objects.exclude(bathroom_last_renovated=None).order_by('bathroom_last_renovated')[
        0].bathroom_last_renovated if Room.objects.all().count() > 0 else 0
    max_renovated_bathroom = Room.objects.exclude(bathroom_last_renovated=None).order_by('-bathroom_last_renovated')[
        0].bathroom_last_renovated if Room.objects.all().count() > 0 else 0
    min_renovated_kitchen = Room.objects.exclude(kitchen_last_renovated=None).order_by('kitchen_last_renovated')[
        0].kitchen_last_renovated if Room.objects.all().count() > 0 else 0
    max_renovated_kitchen = Room.objects.exclude(kitchen_last_renovated=None).order_by('-kitchen_last_renovated')[
        0].kitchen_last_renovated if Room.objects.all().count() > 0 else 0

    accommodation_weeks = 0

    # Iterating through rooms and populating counts.
    for r in Room.objects.all():
        contract_length = r.contract_length
        normalised_size = (min(r.size, 25) - min_size) / (min(max_size, 25) - min_size)
        count_size += (2 * normalised_size - (normalised_size * normalised_size)) * contract_length
        if r.is_ensuite:
            count_ensuite += contract_length
        else:
            count_bathroom += ((5 - r.bathroom_sharing) / 4) * contract_length
        if r.is_double_bed:
            count_double_bed += contract_length
        if r.is_flat:
            count_flat += contract_length
        if not r.faces_lensfield:
            count_facing_lensfield += contract_length
        if r.faces_court:
            count_facing_court += contract_length
        if int(r.floor) != 1:
            count_ground_floor += contract_length
        accommodation_weeks += contract_length
        count_renovated_room += (r.room_last_renovated - min_renovated_room) / (
                max_renovated_room - min_renovated_room) * contract_length
        count_renovated_facilities += ((r.bathroom_last_renovated - min_renovated_bathroom) / (
                max_renovated_bathroom - min_renovated_bathroom) +
                                      (r.kitchen_last_renovated - min_renovated_kitchen) / (
                                              max_renovated_kitchen - min_renovated_kitchen)) / 2 * contract_length

    # Getting weights from settings.
    base_price = float(get_setting('base_price'))
    weight_ensuite = float(get_setting('weight_ensuite'))
    weight_bathroom = float(get_setting('weight_bathroom'))
    weight_double_bed = float(get_setting('weight_double_bed'))
    weight_size = float(get_setting('weight_size'))
    weight_renovated_room = float(get_setting('weight_renovated_room'))
    weight_renovated_facilities = float(get_setting('weight_renovated_facilities'))
    weight_flat = float(get_setting('weight_flat'))
    weight_facing_lensfield = float(get_setting('weight_facing_lensfield'))
    weight_facing_court = float(get_setting('weight_facing_court'))
    weight_ground_floor = float(get_setting('weight_ground_floor'))
    total = float(get_setting('total'))

    # x = Weighted feature weeks.
    x = (weight_ensuite * count_ensuite) + (weight_double_bed * count_double_bed) + (weight_size * count_size) + \
        (weight_bathroom * count_bathroom) + (weight_renovated_room * count_renovated_room) + \
        (weight_renovated_facilities * count_renovated_facilities) + (weight_flat * count_flat) + \
        (weight_facing_lensfield * count_facing_lensfield) + (weight_facing_court * count_facing_court) + \
        (weight_ground_floor * count_ground_floor)

    # y = Feature cost per week.
    y = (total - base_price * accommodation_weeks) / x
    set_setting('feature_price', y)

    # Iterating through rooms and calculating price.
    for room in Room.objects.all():
        with transaction.atomic():
            room_to_update = Room.objects.select_for_update().get(room_id=room.room_id)

            # Calculating sum of weights for this room, and saving in database.
            this_weight = 0

            # Adding weight if ensuite.
            if room_to_update.is_ensuite:
                this_weight += weight_ensuite
                room_to_update.score_ensuite = weight_ensuite
            else:
                score = weight_bathroom * (5 - room_to_update.bathroom_sharing) / 4
                this_weight += score
                room_to_update.score_bathroom = score

            # Adding weight if double bed.
            if room_to_update.is_double_bed:
                this_weight += weight_double_bed
                room_to_update.score_double_bed = weight_double_bed
            else:
                room_to_update.score_double_bed = 0

            # Adding weight if self-contained flat.
            if room_to_update.is_flat:
                this_weight += weight_flat
                room_to_update.score_flat = weight_flat
            else:
                room_to_update.score_flat = 0

            # Adding weight if facing Lensfield Road.
            if not room_to_update.faces_lensfield:
                this_weight += weight_facing_lensfield
                room_to_update.score_facing_lensfield = weight_facing_lensfield
            else:
                room_to_update.score_facing_lensfield = 0

            # Adding weight if facing main court or Domus garden.
            if room_to_update.faces_court:
                this_weight += weight_facing_court
                room_to_update.score_facing_court = weight_facing_court
            else:
                room_to_update.score_facing_court = 0

            # Adding weight if not ground floor room.
            if int(room_to_update.floor) != 1:
                this_weight += weight_ground_floor
                room_to_update.score_ground_floor = weight_ground_floor
            else:
                room_to_update.score_ground_floor = 0

            # Adding weight for size.
            normalised_size = (min(room_to_update.size, 25) - min_size) / (min(max_size, 25) - min_size)
            score_size = weight_size * (2 * normalised_size - (normalised_size * normalised_size))
            this_weight += score_size
            room_to_update.score_size = score_size

            # Adding weight for renovation (room & facilities).
            score_renovated = weight_renovated_room * (room_to_update.room_last_renovated - min_renovated_room) / (
                    max_renovated_room - min_renovated_room)
            this_weight += score_renovated
            room_to_update.score_renovated = score_renovated
            score_renovated_bathroom = (room_to_update.bathroom_last_renovated - min_renovated_bathroom) / (
                    max_renovated_bathroom - min_renovated_bathroom)
            score_renovated_kitchen = (room_to_update.kitchen_last_renovated - min_renovated_kitchen) / (
                    max_renovated_kitchen - min_renovated_kitchen)
            score_renovated_facilities = weight_renovated_facilities * (
                    score_renovated_bathroom + score_renovated_kitchen) / 2
            this_weight += score_renovated_facilities
            room_to_update.score_renovated_facilities = score_renovated_facilities

            # Calculating price based on weight, and saving.
            room_to_update.new_price = this_weight * y + base_price
            room_to_update.score_total = this_weight
            room_to_update.feature_price = this_weight * y
            room_to_update.save()
    round_to_bands()


# ============= ROUND TO BANDS ===================
# Takes the calculated 'new price' and prescribes
# a band, based on closest rounding.

def round_to_bands():
    bands = {}
    for band in Band.objects.all():
        bands[band.weekly_price] = band.band_id
    for room in Room.objects.exclude(new_price=None):
        pricing_notes = ""
        band_price = min(bands, key=lambda x: abs(x - room.new_price))
        if room.size >= 14 and room.is_ensuite:
            band_price = max(band_price, Band.objects.get(band_name="3").weekly_price)
            pricing_notes += "An ensuite room >= 14m2 must be at least Band 3.\n"
        elif room.is_ensuite:
            band_price = max(band_price, Band.objects.get(band_name="4").weekly_price)
            pricing_notes += "An ensuite room must be at least Band 4.\n"
        elif room.identifier.__contains__("LR") and room.floor >= 3:
            band_price = min(band_price, Band.objects.get(band_name="2").weekly_price)
            pricing_notes += "Top floor Lensfield rooms can't be more than Band 2.\n"
        if room.is_flat:
            band_price = Band.objects.get(band_name="1*").weekly_price
            pricing_notes += "Self-contained rooms must be Band 1*.\n"
        if not room.is_flat:
            band_price = min(band_price, Band.objects.get(band_name="1").weekly_price)
        if room.identifier.__contains__("LR") and abs(datetime.datetime.now().year - room.room_last_renovated) >= 10:
            band_price = min(band_price, Band.objects.get(band_name="2").weekly_price)
            pricing_notes += "Lensfield rooms not renovated in the last 10 years cannot be Band 1.\n"
        if room.identifier.__contains__("HL"):
            band_price = Band.objects.get(band_name="1").weekly_price
            pricing_notes += "Howard Lodge all Band 1.\n"
        if room.room_id == 132:
            band_price = Band.objects.get(band_name="3").weekly_price
            pricing_notes += "Inconsistency in House 52 - Room 7 is Band 3."
        new_band = Band.objects.get(band_id=bands[band_price])
        room.pricing_notes = pricing_notes
        room.new_band = new_band
        room.save()


# ========== FIRST YEARS IN BALLOT ===============
# Methods to get the number of first-years who are taking part
# in the ballot, and the number of first-year syndicates.

def get_num_first_years_in_ballot():
    return Student.objects.filter(year=1, in_ballot=True).count()


def get_num_first_year_syndicates():
    return Syndicate.objects.filter(year=1).count()


# ========== SECOND YEARS IN BALLOT ==============
# Methods to get the number of second-years who are
# taking part in the ballot, and the number of
# second-year syndicates.

def get_num_second_years_in_ballot():
    return Student.objects.filter(year=2, in_ballot=True).count()


def get_num_second_year_syndicates():
    return Syndicate.objects.filter(year=2).count()


# =============== SYNDICATE SIZE =================
# Takes a syndicate, and returns the number of
# students who are part of that syndicate.

def get_syndicate_size(syndicate):
    return Student.objects.filter(syndicate=syndicate).count()


def get_num_syndicates():
    return Syndicate.objects.all().count()


# ============= RANDOMISE ORDER ==================
# Randomises the syndicate order for first-years,
# then the order within the syndicates, and updates
# order attribute for each student.
# Has been optimised to reduce database redundancy,
# rather than to run efficiently.

def randomise_order():
    if get_setting('ballot_in_progress') == 'false':
        syndicates = []
        set_setting('randomised', 'false')
        # First check all students either in syndicate or removed from ballot.
        for s in Student.objects.all():
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
                set_setting('randomised', 'true')
            logger.info("Successfully randomised order")
        generate_times()
    else:
        raise BallotInProgressException()


# =============== ADVANCE YEAR ===================
# Converts first-years to second-years, and updates
# ranking to be reverse of that previously. Clears
# ranking of previous second-years, but doesn't
# delete them from Student table.

def advance_year():
    if get_setting('ballot_in_progress') == 'false':
        with transaction.atomic():
            # First clear data pertaining to current second-years.
            second_year_students = Student.objects.select_for_update().filter(year=2)
            for student in second_year_students:
                logger.info("Deleted student [" + student.user_id + "]")
                student.delete()
            second_year_syndicates = Syndicate.objects.select_for_update().filter(year=2)
            for syndicate in second_year_syndicates:
                logger.info("Deleted syndicate [" + str(syndicate.syndicate_id) + "]")
                syndicate.delete()
            # Now convert rankings and update year attributes.
            ranked_first_year_students = Student.objects.select_for_update().filter(year=1, in_ballot=True).order_by(
                '-rank')
            current_rank_student = 1
            for student in ranked_first_year_students:
                student.has_allocated = False
                student.rank = current_rank_student
                student.year = 2
                current_rank_student += 1
                student.save()
                logger.info("Moved student from first to second year [" + student.user_id + "]")
            ranked_first_year_syndicates = Syndicate.objects.select_for_update().filter(year=1).order_by('-rank')
            current_rank_syndicate = 1
            for syndicate in ranked_first_year_syndicates:
                syndicate.rank = current_rank_syndicate
                syndicate.year = 2
                current_rank_syndicate += 1
                syndicate.save()
                logger.info("Moved syndicate from first to second year [" + str(syndicate.syndicate_id) + "]")
            for student in Student.objects.filter(year=1):
                student.year = 2
                student.has_allocated = False
                student.save()
                logger.info("Moved student from first to second year [" + student.user_id + "]")
            for room in Room.objects.exclude(taken_by=None):
                room.taken_by = None
                room.save()
                logger.info("Deallocated room [Room " + str(room.room_id) + "]")
    else:
        raise BallotInProgressException()


# ============ REMOVE FROM BALLOT ================
# Takes a student and removes them from the ballot,
# by removing them from rankings and their syndicate.

def remove_from_ballot(student):
    if get_setting('ballot_in_progress') == 'false':
        with transaction.atomic():
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            student_rank = student_to_update.rank
            student_syndicate = student_to_update.syndicate
            student_to_update.rank = None
            student_to_update.syndicate = None
            student_to_update.accepted_syndicate = False
            student_to_update.in_ballot = False
            student_to_update.save()
            number_in_ballot = Student.objects.order_by('-rank')[0].rank
            # Now decrease rank of all subsequent students.
            if student_rank is not None:
                for rank in range(student_rank + 1, number_in_ballot + 1):
                    st = Student.objects.select_for_update().get(rank=rank)
                    st.rank -= 1
                    st.save()
                logger.info("Removing from ballot - updated succeeding students [" + student.user_id + "]")
            if student_syndicate is not None:
                # If syndicate is now empty, delete it and update ranks.
                if get_syndicate_size(student_syndicate) == 0:
                    syndicate_rank = student_syndicate.rank
                    student_syndicate.delete()
                    logger.info(
                        "Removing from ballot - deleted syndicate [" + str(student_syndicate.syndicate_id) + "]")
                    if syndicate_rank is not None:
                        for rank in range(syndicate_rank + 1, Syndicate.objects.order_by('-rank')[0].rank + 1):
                            sy = Syndicate.objects.select_for_update().get(rank=rank)
                            sy.rank -= 1
                            sy.save()
                        logger.info("Removing from ballot - updated succeeding syndicates")
                else:
                    if student_syndicate.owner_id == student.user_id:
                        reallocate_syndicate_owner(student_syndicate)
                        logger.info(
                            "Removing from ballot - reallocated syndicate owner [" + str(
                                student_syndicate.syndicate_id) + "]")
                    # Check if syndicate complete, and update if necessary.
                    complete = True
                    for student in Student.objects.filter(syndicate=student_syndicate):
                        if not student.accepted_syndicate:
                            complete = False
                            break
                    student_syndicate.complete = complete
                    student_syndicate.save()
                    logger.info("Removing from ballot - succeeded [" + student.user_id + "]")
    else:
        raise BallotInProgressException()


# ============= ADD TO SYNDICATE =================
# Adds a student to the given syndicate. A pre-existing
# syndicate must be specified, then the student will
# be added last in the syndicate.

def add_to_syndicate(student, syndicate):
    if get_setting('ballot_in_progress') == 'false':
        with transaction.atomic():
            syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
            student_to_update = Student.objects.select_for_update().get(user_id=student.user_id)
            syndicate_rank = syndicate_to_update.rank
            # Increments the student rank of all students in subsequent syndicates.
            if syndicate_rank is not None:
                new_rank = 1 + get_num_first_years_in_ballot() + get_num_second_years_in_ballot()
                for rank in range(syndicate_rank + 1, Syndicate.objects.order_by('-rank')[0].rank + 1):
                    sy = Syndicate.objects.get(rank=rank)
                    for st in Student.objects.select_for_update().filter(syndicate=sy):
                        new_rank = min(new_rank, st.rank)
                        st.rank += 1
                        st.save()
                student_to_update.rank = new_rank
            student_to_update.syndicate = syndicate_to_update
            student_to_update.save()
            syndicate_to_update.complete = False
            syndicate_to_update.save()
            logger.info(
                "Added student to syndicate [" + student.user_id + "] [Syndicate " + str(syndicate.syndicate_id) + "]")
    else:
        raise BallotInProgressException()


# ============== ADD AFTER RANK ==================
# Moves rank of individual student to first valid
# position after rank given as argument.
# TODO - this doesn't actually work. Fix it.

def add_after_rank(student, rank):
    if get_setting('ballot_in_progress') == 'false':
        syndicate = Student.objects.get(user_id=student.user_id).syndicate
        if Student.objects.filter(syndicate=syndicate).count() != 1 or syndicate.rank is not None:
            raise ConcurrencyException()
        else:
            with transaction.atomic():
                prior_syndicate = Student.objects.get(rank=rank).syndicate
                for rank in range(Syndicate.objects.order_by('-rank')[0].rank, prior_syndicate.rank, -1):
                    syndicate_to_update = Syndicate.objects.get(rank=rank)
                    syndicate_to_update.rank = syndicate_to_update.rank + 1
                    for student in Student.objects.filter(syndicate=syndicate_to_update):
                        student.rank = student.rank + 1
                        print(student.first_name, student.rank)
                        student.save()
                    syndicate_to_update.save()
                syndicate_to_update = Syndicate.objects.get(syndicate_id=syndicate.syndicate_id)
                syndicate_to_update.rank = prior_syndicate.rank + 1
                syndicate_to_update.save()
                new_rank = (Student.objects.filter(syndicate=prior_syndicate).order_by('-rank')[0]).rank + 1
                print(new_rank)
                student = Student.objects.get(user_id=student.user_id)
                student.rank = new_rank
                student.save()


# ============= CREATE SYNDICATE =================
# Creates a new syndicate, and sends invitations
# to the concerned students.

def create_new_syndicate(student_ids, owner_id):
    if get_setting('ballot_in_progress') == 'false':
        owner = Student.objects.get(user_id=owner_id)
        size = len(student_ids)
        if owner.syndicate is not None or owner.accepted_syndicate or size > 6 or size < 1:
            raise ConcurrencyException()
        else:
            with transaction.atomic():
                syndicate = Syndicate()
                year = Student.objects.get(user_id=owner_id).year
                syndicate.year = year
                syndicate.owner_id = owner_id
                if len(student_ids) == 1:
                    syndicate.complete = True
                syndicate.save()
                for student_id in student_ids:
                    student = Student.objects.select_for_update().get(user_id=student_id)
                    if student.syndicate is not None or student.accepted_syndicate or student.year != year:
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
                logger.info("Created new syndicate [" + str(syndicate.syndicate_id) + "]")
                if not syndicate.complete:
                    invite_syndicate(syndicate)
                else:
                    completed_syndicate(syndicate)
                return syndicate.syndicate_id
    else:
        raise BallotInProgressException()


# ============ DISSOLVE SYNDICATE ================
# Takes a syndicate and dissolves it, updating the
# students' attributes.

def dissolve_syndicate(syndicate):
    if get_setting('ballot_in_progress') == 'true':
        raise BallotInProgressException()
    else:
        failed_syndicate(syndicate)
        with transaction.atomic():
            syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
            for student in Student.objects.select_for_update().filter(syndicate=syndicate_to_update):
                student.syndicate = None
                student.accepted_syndicate = False
                student.save()
            id = syndicate_to_update.syndicate_id
            syndicate_to_update.delete()
            logger.info("Deleted syndicate [" + str(id) + "]")


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
            logger.info("Student accepted syndicate [" + student.user_id + "]")
            syndicate = Syndicate.objects.select_for_update().get(syndicate_id=student_to_update.syndicate.syndicate_id)
            accepted = True
            for s in Student.objects.filter(syndicate=syndicate):
                if not s.accepted_syndicate:
                    accepted = False
            if accepted:
                syndicate.complete = True
                syndicate.save()
                completed_syndicate(syndicate)
            else:
                syndicate.complete = False
                syndicate.save()


# ============= DECLINE SYNDICATE =================
# Takes a user and dissolves the syndicate, sending
# an explanatory email to all members.

def decline_syndicate(student):
    if student.accepted_syndicate:
        raise ConcurrencyException()
    else:
        with transaction.atomic():
            syndicate = Syndicate.objects.select_for_update().get(syndicate_id=student.syndicate.syndicate_id)
            for student in Student.objects.filter(syndicate=syndicate):
                student.syndicate = None
                student.accepted_syndicate = False
                student.save()
                logger.info("Decline syndicate - student removed [" + student.user_id + "]")
            failed_syndicate(syndicate)
            syndicate.delete()


# ======== RE-ALLOCATE SYNDICATE OWNER ============
# Takes a syndicate whose owner has just been removed
# from the ballot, and re-allocates ownership.
# Inductively, syndicate must be non-empty.

def reallocate_syndicate_owner(syndicate):
    if get_setting('ballot_in_progress') == 'false':
        with transaction.atomic():
            students = Student.objects.filter(syndicate=syndicate)
            syndicate_to_update = Syndicate.objects.select_for_update().get(syndicate_id=syndicate.syndicate_id)
            syndicate_to_update.owner_id = students[0].user_id
            syndicate_to_update.save()
            logger.info("Reallocated syndicate owner [" + str(syndicate.syndicate_id) + "]")
    else:
        raise BallotInProgressException()


# =============== GENERATE TIMES ==================
# Takes a start date, and generates the times at which
# each person is to choose their room. Second years on
# the first day, first years on the second.
# Date in datetime format.

def generate_times():
    if get_setting('ballot_in_progress') == 'false':
        with transaction.atomic():
            students = Student.objects.select_for_update().filter(in_ballot=True)
            for s in students:
                s.picks_at = None
                s.save()
        start_date = get_setting('start_date')
        # Generate times for second years.
        dt = datetime.datetime.strptime(start_date + " 09:00", "%d/%m/%y %H:%M")
        with transaction.atomic():
            second_years = Student.objects.select_for_update().filter(year=2, in_ballot=True).exclude(
                rank=None).order_by('rank')
            for student in second_years:
                student.picks_at = dt
                student.save()
                dt += datetime.timedelta(0, 300)

        # Generate times for first years.
        dt = datetime.datetime.strptime(start_date + " 09:00", "%d/%m/%y %H:%M") + datetime.timedelta(1)
        with transaction.atomic():
            first_years = Student.objects.select_for_update().filter(year=1, in_ballot=True).exclude(
                rank=None).order_by('rank')
            for student in first_years:
                student.picks_at = dt
                student.save()
                dt += datetime.timedelta(0, 300)
            logger.info("Successfully generated times")
    else:
        raise BallotInProgressException()


# ========== UPDATE CURRENT STUDENT ==============
# When run, gets student who should be picking
# at current time, and updates setting field.

def update_current_student():
    if get_setting('ballot_in_progress') != 'true':
        raise ConcurrencyException()
    else:
        current_datetime = datetime.datetime.now()
        slot_datetime = current_datetime - datetime.timedelta(minutes=current_datetime.minute % 5,
                                                              seconds=current_datetime.second,
                                                              microseconds=current_datetime.microsecond)
        try:
            student_picking = Student.objects.get(picks_at=slot_datetime)
            while student_picking.has_allocated:
                slot_datetime += datetime.timedelta(minutes=5)
                student_picking = Student.objects.get(picks_at=slot_datetime)
            set_setting('current_student', student_picking.user_id)
            logger.info("Updated currently picking student [" + student_picking.user_id + "]")
        except Student.DoesNotExist:
            set_setting('current_student', None)


# ============ POPULATE STUDENT ================
# Uses the UIS Ibis API to get the given student,
# and if they are not in the database, adds them.

def populate_student(crsid):
    conn = createConnection()
    pm = PersonMethods(conn)
    student = pm.getPerson('crsid', crsid)
    if student != None:
        if Student.objects.filter(user_id=student.identifier.value).count() == 0:
            print("Imported", student.identifier.value, student.registeredName)
            with transaction.atomic():
                s = Student()
                s.user_id = student.identifier.value
                s.first_name = str(student.registeredName).replace(' ' + str(student.surname), '')
                s.surname = student.surname
                s.year = 1
                s.in_ballot = True
                s.has_allocated = False
                s.rank = None
                s.syndicate = None
                s.accepted_syndicate = False
                s.picks_at = None
                s.name_set = False
                s.save()
                logger.info("Added student [" + s.user_id + "]")
        else:
            raise StudentAlreadyExistsException()
    else:
        raise InvalidIdentifierException()


# ============== SEND TO BOTTOM =================
# Changes the given student's picks-at time so
# they are sent to the bottom of the ballot.

def send_to_bottom(student):
    if student.has_allocated:
        raise ConcurrencyException()
    else:
        students_above = Student.objects.filter(year=student.year).exclude(user_id=student.user_id).order_by('picks_at')
        last_student_time = students_above[students_above.count() - 1].picks_at
        new_time = last_student_time + datetime.timedelta(0, 300)
        with transaction.atomic():
            s = Student.objects.select_for_update().get(user_id=student.user_id)
            s.picks_at = new_time
            s.save()
            logger.info("Sent student to bottom of ballot [" + s.user_id + "]")


# =========== GENERATE IDENTIFIERS ==============
# For each room, generates its identifier as per
# College's identification scheme.

def generate_identifiers():
    with transaction.atomic():
        for room in Room.objects.select_for_update().all():
            if room.staircase.identifier is None:
                continue
            prefix = str(room.staircase.identifier)
            numbers = ''.join(c for c in room.room_number if c.isdigit())
            if len(numbers) == 1:
                room.identifier = prefix + "0" + str(room.room_number)
            else:
                room.identifier = prefix + str(room.room_number)
            room.save()
