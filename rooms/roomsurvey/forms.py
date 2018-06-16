from django import forms

from .models import Staircase, Room

"""
FORMS
Defines forms, for example to input room/staircase,
respond to survey, et cetera.
"""

# Form to select staircase.

class StaircaseSelector(forms.Form):
    staircase = forms.ModelChoiceField(queryset=Staircase.objects.all().order_by('name'))


# Form to select room, having selected staircase.

class RoomSelector(forms.Form):
    def __init__(self, *args, **kwargs):
       s = kwargs.pop('staircase')
       super(RoomSelector, self).__init__(*args, **kwargs)
       self.fields['room'] = forms.ModelChoiceField(queryset=Room.objects.all().filter(staircase=s).order_by('room_id'))


# Form to capture survey data.

class SurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        YESNO_CHOICES = (
            (True, 'Yes'),
            (False, 'No')
        )
        self.fields['review'] = forms.Field()
        self.fields['overpriced'] = forms.ChoiceField(choices=YESNO_CHOICES)