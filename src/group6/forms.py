from django import forms

from django import forms
from .models import Words

class WordForm(forms.ModelForm):
    add_to_leitner = forms.BooleanField(
        required=False,
        label="Add to Leitner Box",
    )

    add_to_tick8 = forms.BooleanField(
        required=False,
        label="Add to Tick 8 Box"    )

    class Meta:
        model = Words
        fields = ['word', 'description', 'add_to_leitner', 'add_to_tick8']
        widget = {
            'word': forms.TextInput(attrs={'class': 'position-absolute','placeholder':'کلمه' }),
            'description': forms.Textarea(attrs={'class': 'position-absolute','placeholder':'توضیحات'}),
        }
        labels = {
            'word': 'کلمه',  # متن جدید لیبل
            'description': 'توضیحات',
        }