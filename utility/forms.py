from django import forms

class Compound_interest_form(forms.Form):
    principal = forms.IntegerField()
    interest_rate = forms.FloatField()
    how_many = forms.IntegerField()
    additional = forms.IntegerField(required=False)