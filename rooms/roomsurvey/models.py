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
    room_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30)
    is_ensuite = models.BooleanField()
    is_double_bed = models.BooleanField()
    size = models.IntegerField()
    staircase = models.ForeignKey(Staircase, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


## Model to represent a room review, written by a student.

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=30)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.review_id