from workshops.models import Workshop, Attendance
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from checkin.models import CheckIn
from user.mixins import IsOrganizerMixin, IsVolunteerMixin
from workshops.tables import WorkshopListTable, WorkshopListFilter
from .forms import AddWorkshopForm


## TODO:
# Better fronend...
class WorkshopAdd(IsOrganizerMixin, FormView):
    template_name = 'workshop_add.html'
    success_url = '/workshops/list/'
    form_class = AddWorkshopForm

    def get_context_data(self, **kwargs):
        context = super(WorkshopAdd, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        workshop = form.save(commit=False)
        #valid_time = Workshop.objects.filter()
        workshop.save()
        return super().form_valid(form)


class WorkshopUpdate(IsOrganizerMixin, UpdateView):
    model = Workshop
    success_url = '/workshops/list/'
    fields = ['title', 'description', 'location', 'host', 'open', 'in_person', 'start', 'end']
    template_name = 'workshop_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopUpdate, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        workshop = form.save(commit=False)
        start = form.data['start']
        valid_time = Workshop.objects.filter(start=start)
        print(list(valid_time))
        workshop.save()
        return super(WorkshopUpdate, self).form_valid(form)


class WorkshopList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'workshop_list.html'
    table_class = WorkshopListTable
    filterset_class = WorkshopListFilter
    table_pagination = {'per_page': 100}


## TODO:
# Make a better message for users when workshop/timeslot is not found.
# Better frontend...
class WorkshopDetail(IsVolunteerMixin, DetailView):
    model = Workshop
    template_name = 'workshop_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopDetail, self).get_context_data(**kwargs)
        workshop = kwargs['object']
        attendance = workshop.attendance_set.count()
        # TODO: Make this statement more descriptive.
        if not workshop:
            raise Http404
        context.update({
            'title': workshop.title,
            'description': workshop.description,
            'location': workshop.location,
            'host': workshop.host,
            'start': workshop.start,
            'end': workshop.end,
            'attendance': attendance,  # This is an int
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
        qr_id = request.POST.get('qr_code', None)

        if not qr_id or not workshop_id:
            messages.error(self.request, 'The QR code or workshop is not available.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        workshop = Workshop.objects.filter(id=workshop_id).first()

        if not workshop.open and not self.request.user.is_organizer:
            messages.error(self.request, 'This workshop is not open yet or it has ended.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        hacker_checkin = CheckIn.objects.filter(qr_identifier=qr_id).first()
        if not hacker_checkin:
            messages.error(self.request, 'Invalid QR code!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        hacker = hacker_checkin.application.user
        if not hacker:
            messages.error(self.request, 'No user found for this QR code!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Checks if the user has attended this workshop already. If they have, then a message is displayed.
        hacker_attended = workshop.attendance_set.filter(user=hacker).first()
        if hacker_attended:
            messages.error(self.request, 'This hacker has already been marked for attendance for this workshop!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # Logs user attendance to a workshop.
        attendance = Attendance(workshop=workshop, user=hacker)
        attendance.save()

        messages.success(self.request, 'Hacker attendance logged!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
