from django.shortcuts import render
from workshops.models import Workshop, Timeslot

from django.views.generic.edit import FormView
from user.mixins import IsOrganizerMixin, IsVolunteerMixin
from .forms import AddWorkshopForm
# Create your views here.

class WorkshopAdd(IsOrganizerMixin, FormView):
    template_name = 'workshop_add.html'
    form_class = AddWorkshopForm
    success_url = '#'

    def form_valid(self, form):
        workshop = form.save()
        workshop.save()
        #form.cleaned_data['timeslot'] returns the unique id of the timeslot. this
        #id is then used to get the timeslow object.
        timeslot = Timeslot.objects.get(pk=form.cleaned_data['timeslot'])
        timeslot.workshop = workshop
        timeslot.save()
        return super().form_valid(form)
