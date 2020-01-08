from django import forms
from .models import Workshop, Timeslot

class AddWorkshopForm(forms.ModelForm):

    title = forms.CharField(max_length=63, help_text='Title of the workshop.', label='Workshop Title')

    description = forms.CharField(max_length=300, help_text='Short description of the workshop', label='Workshop description', widget=forms.Textarea(attrs={
        'rows': '4',
    }))

    host = forms.CharField(max_length=63, help_text='If you are affiliated with an organization, please list your organization name.', label='Organization name')

    #Change the __str__ method in the Timeslot model to change how the choices are displayed to users.
    #empty_label set to none because users should NOT be able to add empty timeslots.
    timeslot = forms.ModelChoiceField(queryset=Timeslot.objects.filter(workshop_one__isnull=True) | Timeslot.objects.filter(workshop_two__isnull=True), empty_label=None)

    class Meta:
        model = Workshop
        fields = ['title', 'description', 'host']
