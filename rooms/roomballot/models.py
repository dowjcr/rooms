"""
MODELS
Defines database models to be used in the room ballot application.
Author Cameron O'Connor
"""

from django.db import models


# =================== BAND =======================
# Represents a discrete pricing band.

class Band(models.Model):
    band_id = models.AutoField(primary_key=True)
    band_name = models.CharField(max_length=10)
    weekly_price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "Band " + self.band_name


# ================ SYNDICATE =====================
# Represents a syndicate between Students.

class Syndicate(models.Model):
    YEAR_CHOICES = (
        (1, 'First Ballot Year'),
        (2, 'Second Ballot Year'),
    )

    syndicate_id = models.AutoField(primary_key=True)
    owner_id = models.CharField(max_length=10)
    complete = models.BooleanField(default=False, editable=False)
    year = models.IntegerField(choices=YEAR_CHOICES)
    rank = models.IntegerField(null=True, editable=False)

    def __str__(self):
        return str(self.syndicate_id)


# ================ STAIRCASE =====================
# Represents a staircase. Stores information about
# given staircase, and implements many-to-one
# relationship to PriceCategory.

class Staircase(models.Model):
    staircase_id = models.AutoField(primary_key=True)
    identifier = models.CharField(max_length=10, default=None, null=True)
    name = models.CharField(max_length=30)
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
        (1, 'First Ballot Year'),
        (2, 'Second Ballot Year')
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
    name_set = models.BooleanField(default=True, editable=False)

    def __str__(self):
        return self.first_name + " " + self.surname


# ================== ROOM ========================
# Represents a room. Implements one-to-one
# relationship to Student.

class Room(models.Model):
    FLOOR_CHOICES = (
        (1, 'Ground'),
        (2, 'First'),
        (3, 'Second'),
        (4, 'Third')
    )

    BATHROOM_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5+')
    )

    TYPE_CHOICES = (
        (1, 'JCR Freshers'),
        (2, 'JCR Ballot'),
        (3, 'JCR Outside Ballot'),
        (4, 'MCR')
    )

    # Identifiers.
    room_id = models.AutoField(primary_key=True)
    identifier = models.CharField(max_length=10, default=None, null=True)
    room_number = models.CharField(max_length=10)

    # Room attributes.
    floor = models.IntegerField(choices=FLOOR_CHOICES)
    is_ensuite = models.BooleanField('Has ensuite?', default=False)
    is_double_bed = models.BooleanField('Has double bed?', default=False)
    has_disabled_facilities = models.BooleanField('Has disabled facilities?', default=False)
    room_last_renovated = models.IntegerField('Year Room Last Renovated (YYYY)', null=True)
    bathroom_last_renovated = models.IntegerField('Year Bathroom Last Renovated (YYYY)', null=True)
    kitchen_last_renovated = models.IntegerField('Year Kitchen Last Renovated (YYYY)', null=True)
    faces_lensfield = models.BooleanField('Faces Lensfield Road?', default=False)
    faces_court = models.BooleanField('Faces court/garden?', default=False)
    bathroom_sharing = models.IntegerField(choices=BATHROOM_CHOICES, null=True)
    is_flat = models.BooleanField(default=False)
    size = models.FloatField()
    staircase = models.ForeignKey(Staircase, on_delete=models.SET_DEFAULT, default=None)
    band = models.ForeignKey(Band, on_delete=models.SET_DEFAULT, default=None, null=True)
    type = models.IntegerField(choices=TYPE_CHOICES)
    taken_by = models.ForeignKey(Student, on_delete=models.SET_DEFAULT, editable=False, null=True, default=None)
    price = models.IntegerField(editable=False, default=0)
    new_price = models.FloatField(default=0)

    # Scores for pricing.
    score_ensuite = models.FloatField(editable=False, default=0)
    score_double_bed = models.FloatField(editable=False, default=0)
    score_renovated = models.FloatField(editable=False, default=0)
    score_renovated_facilities = models.FloatField(editable=False, default=0)
    score_bathroom = models.FloatField(editable=False, default=2)
    score_flat = models.FloatField(editable=False, default=0)
    score_facing_lensfield = models.FloatField(editable=False, default=0)
    score_size = models.FloatField(editable=False, default=0)
    score_facing_court = models.FloatField(editable=False, default=0)
    score_ground_floor = models.FloatField(editable=False, default=0)
    score_total = models.FloatField(editable=False, default=0)
    feature_price = models.FloatField(editable=False, default=0)

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
    author_id = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    layout_rating = models.IntegerField()
    facilities_rating = models.IntegerField()
    noise_rating = models.IntegerField()
    overall_rating = models.IntegerField()
    text = models.CharField(max_length=5000)

    def __str__(self):
        return self.room.__str__() + " (Review " + str(self.review_id) + ")"


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
# Stores settings required for app's function.

class Setting(models.Model):
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.key)


# =============== PROXY USER =====================
# Represents a user, not registered as a student, who
# can pick on a student's behalf as their proxy.

class ProxyUser(models.Model):
    user_id = models.CharField('CRSid', primary_key=True, max_length=10)
    first_name = models.CharField('First Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)

    def __str__(self):
        return self.first_name + " " + self.surname


# ============= PROXY INSTANCE ===================
# Represents an instance of someone being able to
# pick as a student's proxy.

class ProxyInstance(models.Model):
    user_id = models.CharField('CRSid of Student', primary_key=True, max_length=10)
    proxy_user_id = models.CharField('CRSid of Proxy', max_length=10)

    def __str__(self):
        return self.proxy_user_id + " picking for " + self.user_id

