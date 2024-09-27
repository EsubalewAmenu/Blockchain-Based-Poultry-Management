from django import forms
from .models import Eggs

class EggsForm(forms.ModelForm):
    class Meta:
        model = Eggs
        fields = ['batchnumber', 'customer', 'breed', 'customercode', 'photo', 'brought', 'returned']