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


class WeightsForm(forms.Form):
    base_price = forms.IntegerField()
    weight_ensuite = forms.IntegerField()
    weight_bathroom = forms.IntegerField()
    weight_double_bed = forms.IntegerField()
    weight_size = forms.IntegerField()
    weight_renovated_room = forms.IntegerField()
    weight_renovated_facilities = forms.IntegerField()
    weight_flat = forms.IntegerField()
    weight_facing_lensfield = forms.IntegerField()
    weight_facing_court = forms.IntegerField()
    weight_ground_floor = forms.IntegerField()
    total = forms.IntegerField()