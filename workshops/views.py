import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.core.serializers.python import Serializer
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from app.mixins import TabsViewMixin
from app.views import TabsView
from applications import models as models_app
from checkin.models import CheckIn
from workshops.models import Workshop, Attended
from workshops.tables import WorkshopsListTable, WorkshopsListFilter, WorkshopsUsersTable, WorkshopsUsersFilter
from user.mixins import IsOrganizerMixin, IsVolunteerMixin

def organizer_tabs(user):
    if user.is_organizer:
        return [('Workshops', reverse('workshops_list'), False),
                ('Users', reverse('workshops_users'), False)]
    return [('Workshops', reverse('workshops_list'), False), ]

class WorkshopsList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'workshops_list.html'
    table_class = WorkshopsListTable
    filterset_class = WorkshopsListFilter
    table_pagination = {'per_page': 100}

    def g_tet_current_tabs(self):
        return organizerabs(self.request.user)

    def get_queryset(self):
        if self.request.user.is_organizer:
            return Workshop.objects.all()
        return Workshop.objects.filter(opened=True)

class WorkshopsUsers(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'workshops_users.html'
    table_class = WorkshopsUsersTable
    filterset_class = WorkshopsUsersFilter
    table_pagination = {'per_page': 100}

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_queryset(self):
        return Attended.objects.all()



class WorkshopDetail(IsOrganizerMixin, TabsView):
    template_name = 'workshop_detail.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(WorkshopDetail, self).get_context_data(**kwargs)
        workshopid = kwargs['id']
        workshop = Workshop.objects.filter(id=workshopid).first()
        if not workshop:
            raise Http404
        context.update({
            'workshop': workshop,
            'location': workshop.location,
            'host': workshop.host,
            'starts': workshop.starts.strftime("%Y-%m-%d %H:%M:%S"),
            'ends': workshop.ends.strftime("%Y-%m-%d %H:%M:%S"),
            'attended': workshop.attended()
        })
        return context

    def post(self, request, *args, **kwargs):
        workshopid = request.POST.get('workshop_id')
        workshop = Workshop.objects.filter(id=workshopid).first()
        workshoptitle = request.POST.get('workshop_title')
        if workshoptitle:
            workshop.title = workshoptitle
        workshoptype = request.POST.get('workshop_type')
        if workshoptype:
            workshop.kind = workshoptype
        workshopstarts = request.POST.get('workshop_starts')
        if workshopstarts:
            workshop.starts = workshopstarts
        workshopends = request.POST.get('workshop_ends')
        if workshopends:
            workshop.ends = workshopends
        workshoptimes = request.POST.get('workshop_times')
        if workshoptimes:
            workshop.times = workshoptimes
        workshopopened = request.POST.get('workshop_opened')
        workshop.opened = (workshopopened == 'opened')
        workshop.save()
        messages.success(self.request, 'workshop updated!')
        return redirect('workshops_list')


class WorkshopAdd(IsOrganizerMixin, TabsView):
    template_name = 'workshop_add.html'

    def get_back_url(self):
        return redirect('workshops_list')

    def get_context_data(self, **kwargs):
        context = super(WorkshopAdd, self).get_context_data(**kwargs)
        context.update({
            'time1': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'time2': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return context

    def post(self, request, *args, **kwargs):
        workshop = Workshop()
        workshoptitle = request.POST.get('workshop_title')
        if workshoptitle:
            workshop.title = workshoptitle
        workshoplocation = request.POST.get('workshop_location')
        if workshoplocation:
            workshop.location= workshoplocation
        workshophost = request.POST.get('workshop_host')
        if workshophost:
            workshop.host= workshophost
        workshopstarts = request.POST.get('workshop_starts')
        if workshopstarts:
            workshop.starts = workshopstarts
        workshopends = request.POST.get('workshop_ends')
        if workshopends:
            workshop.ends = workshopends
        workshopopened = request.POST.get('workshop_opened')
        if workshopopened:
            workshop.opened = (workshopopened == 'opened')
        workshop.save()
        messages.success(self.request, 'workshop added!')
        return redirect('workshops_list')


class WorkshopsCheckin(IsVolunteerMixin, TemplateView):
    template_name = 'workshop_checkin.html'

    def get_context_data(self, **kwargs):
        context = super(WorkshopsCheckin, self).get_context_data(**kwargs)
        workshopid = kwargs['id']
        workshop = Workshop.objects.filter(id=workshopid).first()
        if not workshop:
            raise Http404

        if not workshop.opened and not self.request.user.is_organizer:
            raise PermissionDenied('workshop is not active')

        context.update({
            'workshop': workshop,
        })
        if self.request.GET.get('success', False):
            context.update({
                'success': True,
                'diet': self.request.GET.get('diet', False)
            })
        if self.request.GET.get('error', False):
            context.update({
                'error': self.request.GET.get('error', 'Seems there\'s an error'),
            })
        return context

class WorkshopsCoolAPI(View, IsVolunteerMixin):

    def post(self, request, *args, **kwargs):
        workshopid = request.POST.get('workshop_id', None)
        qrid = request.POST.get('qr_id', None)

        if not qrid or not workshopid:
            return JsonResponse({'error': 'Missing workshop and/or QR. Trying to trick us?'})

        current_workshop = Workshop.objects.filter(id=workshopid).first()
        if not current_workshop.opened and not self.request.user.is_organizer:
            return JsonResponse({'error': 'workshop has been closed. Reach out to an organizer to activate it again'})
        hacker_checkin = CheckIn.objects.filter(qr_identifier=qrid).first()
        if not hacker_checkin:
            return JsonResponse({'error': 'Invalid QR code!'})

        hacker_application = getattr(hacker_checkin, 'application', None)
        if not hacker_application:
            return JsonResponse({'error': 'No application found for current code'})

        checkin = Attended(workshop=current_workshop, user=hacker_application.user)
        checkin.save()

class WorkshopSerializer(Serializer):
    def end_object(self, obj):
        self._current['id'] = obj._get_pk_val()
        self._current['starts'] = str(obj.starts)
        self._current['ends'] = str(obj.ends)
        self._current['attended'] = obj.attended()
        self.objects.append(self._current)
        

class WorkshopsApi(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != settings.WORKSHOPS_TOKEN:
            return HttpResponse(status=500)
        var_object = request.GET.get('object')
        if var_object not in ['workshop']:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid object'}), content_type='application/json')

        workshops = Workshop.objects.filter(ends__gt=datetime.now()).order_by('starts')
        var_all = request.GET.get('all')
        if var_all == '1':
            workshops = Workshop.objects.all().order_by('starts')
        serializer = workshopSerializer()
        workshops_data = serializer.serialize(workshops)
        print(workshops_data)
        return HttpResponse(json.dumps({'code': 0, 'content': workshops_data}), content_type='application/json')

    def post(self, request, format=None):
        var_token = request.GET.get('token')
        if var_token != settings.WORKSHOPS_TOKEN:
            return HttpResponse(status=500)
        var_object = request.GET.get('object')
        if var_object not in ['user', 'workshop']:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid object'}), content_type='application/json')

        var_workshop = request.GET.get('workshop')
        obj_workshop = Workshop.objects.filter(id=var_workshop).first()
        if obj_workshop is None:
            return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid workshop'}), content_type='application/json')
        if var_object == 'user':
            var_repetitions = obj_workshop.times
            var_user = request.GET.get('user')
            obj_checkin = CheckIn.objects.filter(qr_identifier=var_user).first()
            if obj_checkin is None:
                return HttpResponse(json.dumps({'code': 1, 'message': 'Invalid user'}), content_type='application/json')
            obj_application = obj_checkin.application
            obj_user = obj_application.user
            if obj_application is None:
                return HttpResponse(json.dumps({'code': 1, 'message': 'No application found'}),
                                    content_type='application/json')
            var_diet = obj_application.diet
            var_attendeds = Attended.objects.filter(workshop=obj_workshop, user=obj_user).count()
            if var_attendeds >= var_repetitions:
                return HttpResponse(json.dumps({'code': 2, 'message': 'Hacker alreay attended'}),
                                    content_type='application/json')
            obj_attended = Attended()
            obj_attended.workshop = obj_workshop
            obj_attended.user = obj_user
            obj_attended.save()
            return HttpResponse(json.dumps({'code': 0, 'content': {'diet': var_diet}}),
                                content_type='application/json')
        var_repetitions = request.GET.get('times')
        obj_workshop.times = var_repetitions
        obj_workshop.save()
        return HttpResponse(json.dumps({'code': 0, 'message': 'Times updated'}), content_type='application/json')

