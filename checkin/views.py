from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from app.utils import reverse
from app.views import TabsView
from applications.models import Application
from checkin.models import CheckIn
from checkin.tables import ApplicationsCheckInTable, ApplicationCheckinFilter, RankingListTable, \
    ApplicationsReIssueTable
from user.mixins import IsVolunteerMixin, IsOrganizerMixin, IsHackerMixin
from user.models import User


def user_tabs(user):
    return [('List', reverse('check_in_list'), False),
            ('Ranking', reverse('check_in_ranking'), False)]


class CheckInList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsCheckInTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return Application.objects.exclude(status=Application.ATTENDED)

'''
OnlineCheckInHackerView is a class-based view that is specifically tailored towards completely 
online events, such as the case of a pandemic e.g. COVID-19.
    - Back Button will function for both hackers and organizers alike (as it did in the legacy check-in).
    - QR codes are not required for online events, and as a result, are not required for check-in, food,
        workshops, etc.
'''
class OnlineCheckInHackerView(IsHackerMixin, TabsView):
    template_name = 'checkin/online_hacker_checkin.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(OnlineCheckInHackerView, self).get_context_data(**kwargs)
        application_id = kwargs['id']
        application_obj = Application.objects.filter(uuid=application_id).first()
        if not application_obj:
            raise Http404
        context.update({
            'app': application_obj,
            'checkedin': application_obj.status == Application.ATTENDED
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=application_obj).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        # qrcode = request.POST.get('qr_code')
        # if qrcode is None or qrcode == '':
        #     messages.success(self.request, 'The QR code is mandatory!')
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        app = Application.objects.filter(uuid=appid).first()
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        # ci.qr_identifier = qrcode
        ci.save()
        messages.success(self.request, 'Hacker checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckInHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/hacker.html'

    def get_back_url(self):
        return HttpResponseRedirect(reverse('dashboard'))

    def get_context_data(self, **kwargs):
        context = super(CheckInHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        app = Application.objects.filter(uuid=appid).first()
        if not app:
            raise Http404
        context.update({
            'app': app,
            'checkedin': app.status == Application.ATTENDED
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        qrcode = request.POST.get('qr_code')
        if qrcode is None or qrcode == '':
            messages.success(self.request, 'The QR code is mandatory!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        app = Application.objects.filter(uuid=appid).first()
        app.check_in()
        ci = CheckIn()
        ci.user = request.user
        ci.application = app
        ci.qr_identifier = qrcode
        ci.save()
        messages.success(self.request, 'Hacker checked-in! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class CheckinRankingView(TabsViewMixin, IsOrganizerMixin, SingleTableMixin, TemplateView):
    template_name = 'checkin/ranking.html'
    table_class = RankingListTable

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return User.objects.annotate(
            checkin_count=Count('checkin__application')).exclude(checkin_count=0)


class ReIssueList(IsVolunteerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'checkin/list.html'
    table_class = ApplicationsReIssueTable
    filterset_class = ApplicationCheckinFilter
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return user_tabs(self.request.user)

    def get_queryset(self):
        return Application.objects.filter(status=Application.ATTENDED)


class ReIssueHackerView(IsVolunteerMixin, TabsView):
    template_name = 'checkin/reissue.html'

    def get_back_url(self):
        return 'javascript:history.back()'

    def get_context_data(self, **kwargs):
        context = super(ReIssueHackerView, self).get_context_data(**kwargs)
        appid = kwargs['id']
        app = Application.objects.filter(uuid=appid).first()
        ci = CheckIn.objects.get(application=app)
        if not app:
            raise Http404
        context.update({
            'app': app,
            'checkedin': app.status == Application.ATTENDED,
            'ci': ci
        })
        try:
            context.update({'checkin': CheckIn.objects.filter(application=app).first()})
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        appid = request.POST.get('app_id')
        qrcode = request.POST.get('qr_code')
        if qrcode is None or qrcode == '':
            messages.success(self.request, 'The QR code is mandatory!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        app = Application.objects.filter(uuid=appid).first()

        ci = CheckIn.objects.get(application=app)
        ci.qr_identifier = qrcode
        ci.save()

        messages.success(self.request, 'Hacker re-issued! Good job! '
                                       'Nothing else to see here, '
                                       'you can move on :D')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
