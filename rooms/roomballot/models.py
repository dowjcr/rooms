"""
MODELS
Defines database models to be used in the room ballot application.
Author Cameron O'Connor
"""

from django.db import models


# ============== PRICE CATEGORY ==================
# Represents a price category.
# TODO: finalise pricing standard, and store required information here.

class PriceCategory(models.Model):
    category_id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.category_id)


# ================ SYNDICATE =====================
# Represents a syndicate between Students.

class Syndicate(models.Model):
    YEAR_CHOICES = (
        (1, 'First Ballot Year'),
        (2, 'Second Ballot Year')
    )

    syndicate_id = models.AutoField(primary_key=True)
    owner_id = models.CharField(max_length=10)
    complete = models.BooleanField(default=False)
    year = models.IntegerField(choices=YEAR_CHOICES)
    rank = models.IntegerField(null=True)

    def __str__(self):
        return str(self.syndicate_id)


# ================ STAIRCASE =====================
# Represents a staircase. Stores information about
# given staircase, and implements many-to-one
# relationship to PriceCategory.

class Staircase(models.Model):
    staircase_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    price_category = models.ForeignKey(PriceCategory, on_delete=models.SET_DEFAULT, default=None)
    contract_length = models.IntegerField('Number of contract weeks?')
    description = models.CharField(max_length=1000, default=None, null=True, blank=True)

    def __str__(self):
        return self.name


# ================== STUDENT =====================
# Stores user information, and implements many-to-one
# relationship to Syndicate. Note that user_id
# corresponds to CRSid.

class Student(models.Model):
    YEAR_CHOICES = (
        (1, 'Currently First Year'),
        (2, 'Currently Second Year')
    )

    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    year = models.IntegerField(choices=YEAR_CHOICES)
    in_ballot = models.BooleanField(default=True, editable=False)
    has_allocated = models.BooleanField(default=False, editable=False)
    rank = models.IntegerField(null=True, blank=True, editable=False)
    syndicate = models.ForeignKey(Syndicate, on_delete=models.SET_DEFAULT, default=None, null=True, editable=False)
    accepted_syndicate = models.BooleanField(default=False, editable=False)
    picks_at = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.first_name + " " + self.surname


# ================== ROOM ========================
# Represents a room. Implements one-to-one
# relationship to Student.

class Room(models.Model):
    BAND_CHOICES = (
        (1, 'Band 1'),
        (2, 'Band 2'),
        (3, 'Band 3'),
        (4, 'Band 4'),
        (5, 'Band 5'),
        (6, 'Band 6')
    )

    FLOOR_CHOICES = (
        (1, 'Ground'),
        (2, 'First'),
        (3, 'Second'),
        (4, 'Third')
    )

    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10)
    floor = models.IntegerField(choices=FLOOR_CHOICES)
    is_ensuite = models.BooleanField('Has ensuite?')
    is_double_bed = models.BooleanField('Has double bed?')
    has_disabled_facilities = models.BooleanField('Has disabled facilities?')
    size = models.FloatField()
    staircase = models.ForeignKey(Staircase, on_delete=models.SET_DEFAULT, default=None)
    band = models.IntegerField(choices=BAND_CHOICES)
    taken_by = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, null=True, editable=False, default=None)
    price = models.IntegerField(editable=False, default=0)
    sort_number = models.IntegerField(default=0)

    def __str__(self):
        return self.staircase.__str__() + ", Room " + str(self.room_number)


# ================== REVIEW ======================
# Stores reviews which users have left for a particular
# room. Implements many-to-one relationship with Room.

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.SET_DEFAULT, default=None)
    author_name = models.CharField(max_length=40)
    text = models.CharField(max_length=1000)
    # TODO: add review attributes as required.

    def __str__(self):
        return self.room.__str__() + ", Review " + str(self.review_id)


# =================== ADMIN ======================
# Stores information about users who are authorised
# to access the backend management system.

class AdminUser(models.Model):
    entry_id = models.AutoField(primary_key=True)
    user_id = models.CharField('CRSid', max_length=10)
    role = models.CharField(max_length=30)

    def __str__(self):
        return self.user_id


# =================== IMAGE ======================
# Implements relationship allowing storage of image
# files for room.

class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.SET_DEFAULT, default=None)
    thumbnail = models.ImageField(upload_to='room_images')
    file = models.ImageField(upload_to='room_images')

    def __str__(self):
        return self.room.__str__() + " (Image " + str(self.image_id) + ")"


# ================ FLOORPLAN =====================
# Implements relationship allowing storage of floorplan
# files for staircase.

class Floorplan(models.Model):
    floorplan_id = models.AutoField(primary_key=True)
    staircase = models.ForeignKey(Staircase, on_delete=models.SET_DEFAULT, default=None)
    file = models.FileField(upload_to='floorplans')

    def __str__(self):
        return self.staircase.__str__() + " (Floorplan " + str(self.floorplan_id) + ")"


# ================== SETTING =====================
# Stores settings required for app's function, using
# django-modeldict-yplan.

class Setting(models.Model):
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.key)