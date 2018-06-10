from django import forms

from .models import Staircase, Room

"""
FORMS
Defines forms, for example to input room/staircase,
respond to survey, et cetera.
"""

# Form to select staircase.
class StaircaseSelector(forms.Form):
    staircase = forms.ModelChoiceField(queryset=Staircase.objects.all())


# Form to select room, having selected staircase.
class RoomSelector(forms.Form):
    def __init__(self, *args, **kwargs):
       sc = kwargs.pop('staircase')
       super(RoomSelector, self).__init__(*args, **kwargs)
       self.fields["room"] = forms.ModelChoiceField(queryset=Room.objects.all().filter(staircase=sc))