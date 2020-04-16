from django import forms
from .models import SponsorApplication, Sponsor, TSHIRT_SIZES, DIETS, TIERS

class SponsorForm(forms.ModelForm):
    tshirt_size = forms.TypedChoiceField(choices=TSHIRT_SIZES)

    diet = forms.TypedChoiceField(choices=DIETS)

    other_diet = forms.CharField(max_length=255,required=False,help_text='If you selected "Others" above, please describe your dietary restrictions in this field.')

    company_logo = forms.ImageField(required=False, help_text="We would highly appreciate if you could upload your company's logo (preferably in .svg or .png format) in order to speed up the process of getting your company's logo onto our site.")

    class Meta:
        model = SponsorApplication
        fields = ['tshirt_size', 'diet', 'other_diet', 'company_logo']

class SponsorAddForm(forms.ModelForm):
    company = forms.CharField(max_length=255, label='Company Name')

    email_domain = forms.CharField(max_length=255, label='Email Domain', help_text='ex: ugahacks.com')

    tier = forms.TypedChoiceField(choices=TIERS, label='Tier')

    class Meta:
        model = Sponsor
        fields = ['company', 'email_domain', 'tier']
