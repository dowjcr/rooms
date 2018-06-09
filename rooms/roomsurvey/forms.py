from django import forms

from .models import Staircase, Room

class StaircaseSelector(forms.Form):
    staircase = forms.ModelChoiceField(queryset=Staircase.objects.all())

class RoomSelector(forms.Form):
    room = forms.ModelChoiceField(queryset=Room.objects.all())