from django.shortcuts import render
from workshops.models import Workshop, Timeslot

from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView

from user.mixins import IsOrganizerMixin, IsVolunteerMixin
from .forms import AddWorkshopForm

#To do:
#New AddWorkshopForm instance isnt being created everytime this view is accessed (I think). Does not refresh the list of
#timeslots to choose from. Need to figure out fix.
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

class WorkshopList(IsVolunteerMixin, ListView):
    template_name = 'workshop_list.html'
    context_object_name = 'workshops'
    #Change pagination accordingly as needed.
    paginate_by = 100
    def get_queryset(self):
        #Add ordering if needed
        workshops = Workshop.objects.all()
        return workshops

class WorkshopDetail(IsOrganizerMixin, DetailView):
    model = Workshop

    def get_context_data(self, **kwargs):
        context = super(WorkshopDetail, self).get_context_data(**kwargs)
        workshopid = kwargs['id']
        workshop = Workshop.objects.filter(id=workshopid).first()
        #Since workshop is a ForeignKey in timeslot, the start and end attributes are retrieved from
        #the timeslot model.
        timeslot = Timeslot.objects.filter(workshop=workshop).first()
        if not workshop or not timeslot:
            raise Http404
        context.update({
            'title': workshop.title,
            'location': workshop.location,
            'host': workshop.host,
            'start': timeslot.start,
            'end': timeslot.end,
            #Todo:
            #Attended model is implemented in the previous workshop app, but has not been rebuilt yet.
            #'attended': workshop.attended(),
        })
        return context
