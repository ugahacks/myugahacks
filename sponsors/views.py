from .forms import SponsorForm, AddSponsorForm
from .tables import ApplicationsListSponsor
from organizers.views import ApplicationDetailView
from applications.models import Application

from app.mixins import TabsViewMixin
from django_tables2.export import ExportMixin
from django_tables2 import SingleTableMixin

from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse

class SponsorApplication(FormView):
    template_name = 'sponsor_application.html'
    success_url = ''
    form_class = SponsorForm

    def form_valid(self, form):
        sponsor_application = form.save()
        return super().form_valid(form)

class AddSponsor(FormView):
    template_name = 'add_sponsor.html'
    success_url = ''
    form_class = AddSponsorForm

    def form_valid(self, form):
        sponsor = form.save()
        return super().form_valid(form)


class SponsorHomePage(TabsViewMixin, ExportMixin, SingleTableMixin, ListView):
    template_name = 'sponsor_home.html'
    table_class = ApplicationsListSponsor
    table_pagination = {'per_page': 50}
    exclude_columns = ('detail', 'status', 'vote_avg')
    export_name = 'applications'

    def get_queryset(self):
        return Application.objects.all().filter(participant='Hacker')

class ApplicationDetailViewSponsor(ApplicationDetailView):
    def get_back_url(self):
        return reverse('sponsor_home')
