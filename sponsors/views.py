from django.shortcuts import render
from .forms import SponsorForm, AddSponsorForm
from django.views.generic.edit import FormView
# Create your views here.

class SponsorApplication(FormView):
    template_name = 'sponsor_application.html'
    success_url = ''
    form_class = SponsorForm

class AddSponsor(FormView):
    template_name = 'add_sponsor.html'
    success_url = ''
    form_class = AddSponsorForm
