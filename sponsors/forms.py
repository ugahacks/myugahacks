from django import forms
from .models import SponsorApplication, Sponsor, TSHIRT_SIZES, DIETS, TIERS

class SponsorForm(forms.ModelForm):
    tshirt_size = forms.TypedChoiceField(choices=TSHIRT_SIZES)

    diet = forms.TypedChoiceField(choices=DIETS)

    company_logo = forms.ImageField()

    class Meta:
        model = SponsorApplication
        fields = ['tshirt_size', 'diet', 'company_logo']

class AddSponsorForm(forms.ModelForm):
    company = forms.CharField(max_length=255, label='Company Name')

    email_domain = forms.CharField(max_length=255, label='Email Domain', help_text='ex: @ugahacks.com')

    tier = forms.TypedChoiceField(choices=TIERS, label='Tier')

    class Meta:
        model = Sponsor
        fields = ['company', 'email_domain', 'tier']
        
