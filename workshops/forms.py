from django import forms
from .models import Workshop, Timeslot

class AddWorkshopForm(forms.ModelForm):

    title = forms.CharField(max_length=63, help_text='Title of the workshop.', label='Workshop Title')

    description = forms.CharField(max_length=300, help_text='Short description of the workshop', label='Workshop description', widget=forms.Textarea(attrs={
        'rows': '4',
    }))

    host = forms.CharField(max_length=63, help_text='If you are affiliated with an organization, please list your organization name.', label='Organization name')

    #Dropdown field where choices are available timeslots to register a workshop.
    #Available timeslows are defined by whether the Timeslot.workshop field is
    #empty (null) or not.
    #NOTE: The value of the choices are the timeslow id's. For passing in the
    #timeslot object itself would not work. If you could get it to work, go
    #for it.
    timeslot = forms.ChoiceField(choices=[(ts.id, str(ts)) for ts in Timeslot.objects.filter(workshop__isnull=True)])

    class Meta:
        model = Workshop
        fields = ['title', 'description', 'host']
