# forms.py
from django import forms
from .models import Event
from .models import Account

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['title', 'amount', 'date']
