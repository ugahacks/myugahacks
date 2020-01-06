from django.shortcuts import render
from workshops.models import Workshop, Timeslot
from django.http import Http404

from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView

from user.mixins import IsOrganizerMixin, IsVolunteerMixin
from .forms import AddWorkshopForm

#TODO:
#Add message (or redirect w/ different context) when there are no more timeslots available.
class WorkshopAdd(IsOrganizerMixin, FormView):
    template_name = 'workshop_add.html'
    success_url = '#'
    form_class = AddWorkshopForm

    def form_valid(self, form):
        workshop = form.save()
        workshop.save()
        #form.cleaned_data['timeslot'] returns the unique id of the timeslot. this
        #id is then used to get the timeslow object.
        #timeslot = Timeslot.objects.get(pk=form.cleaned_data['timeslot'])
        timeslot = form.cleaned_data['timeslot']
        timeslot.workshop = workshop
        timeslot.save()
        return super().form_valid(form)

class WorkshopList(IsVolunteerMixin, ListView):
    template_name = 'workshop_list.html'
    context_object_name = 'workshops'
    #Change pagination accordingly as needed.
    paginate_by = 100
    def get_queryset(self):
        #Add ordering if needed
        workshops = Workshop.objects.all()
        return workshops

## TODO:
#Make a better message for users when workshop/timeslot is not found.
class WorkshopDetail(IsOrganizerMixin, DetailView):
    model = Workshop
    template_name = 'workshop_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopDetail, self).get_context_data(**kwargs)
        workshop = kwargs['object']
        #workshopid = kwargs['object']
        #workshop = Workshop.objects.get(pk=workshopid)
        #Since workshop is a ForeignKey in timeslot, the start and end attributes are retrieved from
        #the timeslot model.
        #There should only be one workshop per timeslot. Gets the timeslot related to the given workshop.
        timeslot = workshop.timeslot_set.first()
        if not workshop or not timeslot:
            raise Http404
        context.update({
            'title': workshop.title,
            'description': workshop.description,
            'location': workshop.location,
            'host': workshop.host,
            'start': timeslot.start,
            'end': timeslot.end,
            #Todo:
            #Attended model is implemented in the previous workshop app, but has not been rebuilt yet.
            #'attended': workshop.attended(),
        })
        return context
