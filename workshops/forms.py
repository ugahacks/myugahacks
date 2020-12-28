from django import forms

from .models import Workshop

import datetime


class AddWorkshopForm(forms.ModelForm):
    title = forms.CharField(max_length=63, label='Workshop Title')

    description = forms.CharField(max_length=300, label='Workshop description', widget=forms.Textarea(attrs={
        'rows': '4',
        'style': 'resize:none;',
    }))

    location = forms.CharField(max_length=63, label='Location')

    host = forms.CharField(max_length=63, label='Organization name')

    in_person = forms.BooleanField(label = 'In person?', required=False)

    points = forms.IntegerField(initial=0)

    start = forms.DateTimeField(initial=datetime.date.today)

    end = forms.DateTimeField(initial=datetime.date.today)

    class Meta:
        model = Workshop
        fields = ['title', 'description', 'location', 'host', 'points', 'in_person', 'start', 'end']
