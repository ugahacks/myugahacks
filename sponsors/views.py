from django.shortcuts import render
from .forms import SponsorForm, AddSponsorForm
from django.views.generic.edit import FormView
# Create your views here.

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
