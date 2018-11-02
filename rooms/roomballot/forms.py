from django import forms

class ReviewForm(forms.Form):
    title = forms.CharField()
    layout_rating = forms.IntegerField()
    facilities_rating = forms.IntegerField()
    noise_rating = forms.IntegerField()
    overall_rating = forms.IntegerField()
    text = forms.CharField()

class FirstNameForm(forms.Form):
    first_name = forms.CharField()