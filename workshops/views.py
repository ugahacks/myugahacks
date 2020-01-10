from django.shortcuts import render
from workshops.models import Workshop, Timeslot, Attendance
from django.http import Http404, JsonResponse

from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, TemplateView

from user.mixins import IsOrganizerMixin, IsVolunteerMixin
from .forms import AddWorkshopForm

from checkin.models import CheckIn
## TODO:
# make sure to display different content when there are no available timeslots in html template.
class WorkshopAdd(IsOrganizerMixin, FormView):
    template_name = 'workshop_add.html'
    success_url = '#'
    form_class = AddWorkshopForm

    #use {% if is_available %} in html template to check if there are any timeslots available. If not, do not display the form.
    #This method is used to check whether or not there are timeslots available.
    def get_context_data(self, **kwargs):
        context = super(WorkshopAdd, self).get_context_data(**kwargs)
        if (Timeslot.objects.filter(workshop_one__isnull=True).count() + Timeslot.objects.filter(workshop_two__isnull=True).count()) > 0:
            context.update({
                'is_available': True,
            })
        else:
            context.update({
                'is_available': False,
            })
        return context

    def form_valid(self, form):
        workshop = form.save()
        workshop.save()
        #form.cleaned_data['timeslot'] returns the unique id of the timeslot. this
        #id is then used to get the timeslow object.
        #timeslot = Timeslot.objects.get(pk=form.cleaned_data['timeslot'])
        timeslot = form.cleaned_data['timeslot']
        #Checks if workshop_one is filled first.
        if not timeslot.workshop_one:
            timeslot.workshop_one = workshop
        else:
            timeslot.workshop_two = workshop
        timeslot.save()
        return super().form_valid(form)

## TODO:
#Add user filtering and search functionality.
class WorkshopList(IsVolunteerMixin, ListView):
    template_name = 'workshop_list.html'
    context_object_name = 'workshops'
    #Change pagination accordingly as needed.
    paginate_by = 100
    def get_queryset(self):
        #Maybe add ordering based off of the the timeslot. Not sure how to do this right now since it would be a reverse forgign key.
        workshops = Workshop.objects.all().order_by('-open')
        return workshops

## TODO:
#Make a better message for users when workshop/timeslot is not found.
class WorkshopDetail(IsOrganizerMixin, DetailView):
    model = Workshop
    template_name = 'workshop_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopDetail, self).get_context_data(**kwargs)
        workshop = kwargs['object']
        #Since workshop is a ForeignKey in timeslot, the start and end attributes are retrieved from
        #the timeslot model.
        #There should only be two workshops per timeslot. Gets the timeslot related to the given workshop.
        timeslot = workshop.workshop_one_set.first() or workshop.workshop_two_set.first()
        #Recieves the total amount of people that attended this workshop
        attendance = workshop.attendance_set.count()
        #TODO: Make this statement more descriptive.
        if not workshop or not timeslot:
            raise Http404
        context.update({
            'title': workshop.title,
            'description': workshop.description,
            'location': workshop.location,
            'host': workshop.host,
            'start': timeslot.start,
            'end': timeslot.end,
            'attendance': attendance, #This is an int
        })
        return context

class WorkshopCheckin(IsVolunteerMixin, TemplateView):
    template_name = 'workshop_checkin.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopCheckin, self).get_context_data(**kwargs)
        workshopid = kwargs['id']
        workshop = Workshop.objects.filter(id=workshopid).first()
        if not workshop:
            raise Http404

        if not workshop.open and not self.request.user.is_organizer:
            raise PermissionDenied('Meal is not active')

        context.update({
            'workshop': workshop,
        })
        if self.request.GET.get('success', False):
            context.update({
                'success': True,
            })
        if self.request.GET.get('error', False):
            context.update({
                'error': self.request.GET.get('error', 'Seems there\'s an error'),
            })
        return context

    def post(self, request, *args, **kwargs):
        workshop_id = request.POST.get('workshop_id', None)
        qr_id = request.POST.get('qr_id', None)

        if not qr_id or not workshop_id:
            return JsonResponse({'error': 'QR or workshop is not available.'})

        workshop = Workshop.objects.filter(id=workshop_id).first()

        if not workshop.open and not self.request.user.is_organizer:
            return JsonResponse({'error': 'Workshop is not open yet or it has already ended.'})

        hacker_checkin = CheckIn.objects.filter(qr_identifier=qr_id).first()
        if not hacker_checkin:
            return JsonResponse({'error': 'Invalid QR code!'})
        #Not sure what this line is for.
        hacker_application = getattr(hacker_checkin, 'application', None)
        if not hacker_application:
            return JsonResponse({'error': 'No application found for current code'})
        #Checks if the user has attended this workshop already. If they have, then a message is displayed.
        hacker_attended = workshop.attendance_set().filter(user=hacker_application.user).first()
        if hacker_attended:
            return JsonResponse({'error': 'Hacker has already checked in for this workshop'})

        #Logs user attendance to a workshop.
        attendance = Attendance(workshop=workshop, user=hacker_application.user)
        attendance.save()

        return JsonResponse({'success': True})
