from django.db import models

"""
MODELS
Defines database models to be used in this simple survey
application, to get room metadata.
"""

## Model to represent a staircase, currently only with a name attribute.

class Staircase(models.Model):
    staircase_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


## Model to represent a room, with various attributes. Note that
## size is stored as an Integer, to be divided by 100.

class Room(models.Model):
    BAND_CHOICES = (
        (1, 'Band 1'),
        (2, 'Band 2'),
        (3, 'Band 3'),
        (4, 'Band 4'),
        (5, 'Band 5'),
        (6, 'Band 6')
    )
    
    room_id = models.CharField('Room ID', max_length=10, primary_key=True)
    room_number = models.IntegerField()
    is_ensuite = models.BooleanField('Has Ensuite?')
    is_double_bed = models.BooleanField('Has Double Bed?')
    size = models.FloatField()
    staircase = models.ForeignKey(Staircase, on_delete=models.CASCADE)
    band = models.IntegerField(choices=BAND_CHOICES)

    def __str__(self):
        return self.staircase.__str__() + ", Room " + str(self.room_number)


## Model to represent a room review, written by a student.

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=30)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.review_id


## Model to represent a survey response.

class SurveyResponse(models.Model):
    response_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=30)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    overpriced = models.BooleanField()
    important_factors = models.CharField(max_length=200)

    def __str__(self):
        return self.response_id