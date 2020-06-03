from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from app.mixins import TabsViewMixin
from applications.models import Application
from organizers.views import ApplicationDetailView
from user.mixins import IsOrganizerMixin, IsSponsorMixin
from .forms import SponsorForm, SponsorAddForm
from .models import Sponsor, SponsorApplication
from .tables import ApplicationsListSponsor, SponsorListTable, SponsorListFilter


class SponsorApplicationView(FormView, IsSponsorMixin):
    template_name = 'sponsor_application.html'
    success_url = reverse_lazy('sponsors:sponsor_home')
    form_class = SponsorForm

    def form_valid(self, form):
        sponsor_application = form.save(commit=False)
        sponsor_application.user = self.request.user
        sponsor_application.save()
        return super().form_valid(form)


class SponsorAdd(FormView, IsOrganizerMixin):
    template_name = 'sponsor_add.html'
    success_url = reverse_lazy('sponsors:sponsor_list')
    form_class = SponsorAddForm

    def form_valid(self, form):
        sponsor = form.save()
        return super().form_valid(form)


class SponsorUpdate(IsOrganizerMixin, UpdateView):
    model = Sponsor
    success_url = reverse_lazy('sponsors:sponsor_list')
    fields = ['company', 'email_domain', 'tier']
    template_name = 'sponsor_update.html'

    def form_valid(self, form):
        sponsor = form.save()
        return super(SponsorUpdate, self).form_valid(form)


class SponsorList(TabsViewMixin, SingleTableMixin, FilterView, IsOrganizerMixin):
    template_name = 'sponsor_list.html'
    table_class = SponsorListTable
    filterset_class = SponsorListFilter
    table_pagination = {'per_page': 100}


class SponsorHomePage(TabsViewMixin, ExportMixin, SingleTableMixin, ListView, IsSponsorMixin):
    template_name = 'sponsor_home.html'
    table_class = ApplicationsListSponsor
    table_pagination = {'per_page': 50}
    exclude_columns = ('detail', 'status', 'vote_avg')
    export_name = 'applications'

    def get_context_data(self, **kwargs):
        context = super(SponsorHomePage, self).get_context_data(**kwargs)
        has_application = SponsorApplication.objects.filter(user=self.request.user)
        context.update({
            'has_application': has_application,
        })
        return context

    def get_queryset(self):
        return Application.objects.all().filter(participant='Hacker')


class ApplicationDetailViewSponsor(ApplicationDetailView, IsSponsorMixin):
    def get_back_url(self):
        return reverse('sponsors:sponsor_home')


class SponsorScannedList(SponsorHomePage):

    def get_context_data(self, **kwargs):
        context = super(SponsorScannedList, self).get_context_data(**kwargs)
        has_application = SponsorApplication.objects.filter(user=self.request.user)
        context.update({
            'has_application': has_application,
        })
        return context

    def get_queryset(self):
        domain = self.request.user.email.split('@')[1]
        sponsor = Sponsor.objects.filter(email_domain=domain).first()
        scanned = sponsor.scanned_hackers.all()
        users = []
        for user in scanned:
            users.append(user)
        return Application.objects.all().filter(user__in=users)
