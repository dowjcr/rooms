"""
MODELS
Defines database models to be used in the room ballot application.
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
        (1, 'Current First Year'),
        (2, 'Current Second Year')
    )

    syndicate_id = models.AutoField(primary_key=True)
    year = models.IntegerField(choices=YEAR_CHOICES)
    rank = models.IntegerField(editable=False)

    def __str__(self):
        return str(self.syndicate_id)


# ================ STAIRCASE =====================
# Represents a staircase. Stores information about
# given staircase, and implements many-to-one
# relationship to PriceCategory.

class Staircase(models.Model):
    staircase_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    price_category = models.ForeignKey(PriceCategory, on_delete=models.CASCADE)
    contract_length = models.IntegerField('Number of contract weeks?')

    def __str__(self):
        return self.name


# ================== STUDENT =====================
# Stores user information, and implements many-to-one
# relationship to Syndicate. Note that user_id
# corresponds to CRSid.

class Student(models.Model):
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    in_ballot = models.BooleanField()
    has_allocated = models.BooleanField()
    rank = models.IntegerField(editable=False)
    syndicate = models.ForeignKey(Syndicate, on_delete=models.CASCADE)
    accepted_syndicate = models.BooleanField()

    def __str__(self):
        return self.user_id


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
    staircase = models.ForeignKey(Staircase, on_delete=models.CASCADE)
    band = models.IntegerField(choices=BAND_CHOICES)
    taken = models.BooleanField('Has been allocated?')
    taken_by = models.ForeignKey(Student, on_delete=models.CASCADE)
    price = models.IntegerField(editable=False)

    def __str__(self):
        return self.staircase.__str__() + ", Room " + str(self.room_number)


# ================== REVIEW ======================
# Stores reviews which users have left for a particular
# room. Implements many-to-one relationship with Room.

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # TODO: add review attributes as required.

    def __str__(self):
        return self.room.__str__() + str(self.review_id)


# =================== ADMIN ======================
# Stores information about users who are authorised
# to access the backend management system.

class AdminUser(models.Model):
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    role = models.CharField()

    def __str__(self):
        return self.user_id


# =================== IMAGE ======================
# Implements relationship allowing storage of image
# files for room.

class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='room_images')

    def __str__(self):
        return self.room.__str__() + str(self.image_id)