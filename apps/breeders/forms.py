from django import forms
from .models import Breeders

class BreedersForm(forms.ModelForm):
    class Meta:
        model = Breeders
        fields = '__all__'
