from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from form_utils.forms import BetterModelForm

from app.mixins import OverwriteOnlyModelFormMixin
from app.utils import validate_url
from applications import models

YEARS = [x for x in range(1930, 2021)]


class ApplicationForm(OverwriteOnlyModelFormMixin, BetterModelForm):
    github = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://github.com/byte'}))
    devpost = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://devpost.com/byte'}))
    linkedin = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'https://www.linkedin.com/in/byte'}))
    site = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'https://byte.build'}))
    phone_number = forms.CharField(required=True, label='What phone number should we contact in case of an emergency?',
                                   help_text='We will use this number solely for emergency purposes.',
                                   widget=forms.TextInput(
                                       attrs={'class': 'form-control', 'placeholder': '(###) ###-####'}))
    university = forms.CharField(required=True,
                                 label='What university do you study at?',
                                 help_text='Current or most recent school you attended.',
                                 widget=forms.TextInput(
                                     attrs={'class': 'typeahead-schools', 'autocomplete': 'off'}))

    degree = forms.CharField(required=True, label='What\'s your major/degree?',
                             help_text='Current or most recent degree you\'ve received',
                             widget=forms.TextInput(
                                 attrs={'class': 'typeahead-degrees', 'autocomplete': 'off'}))

    first_timer = forms.TypedChoiceField(
        required=True,
        label='Will %s be your first hackathon?' % settings.HACKATHON_NAME,
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    first_ugahacks = forms.TypedChoiceField(
        required=True,
        label='Have you attended any previous UGAHacks?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect
    )

    reimb = forms.TypedChoiceField(
        required=False,
        label='Would you like to apply for travel reimbursement?',
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')),
        initial=False,
        widget=forms.RadioSelect
    )

    ethnicity = forms.TypedChoiceField(
        required=False,
        label='What race/ethnicity do you identify with?',
        choices=(('amIndian', 'American Indian or Alaskan Native'), ('asian', 'Asian/Pacific Islander'),
                 ('aAm', 'Black or African American'), ('hispanic', 'Hispanic'), ('white', 'White or Caucasian'),
                 ('multiple', 'Multiple ethnicities/Other'), ('noAnswer', 'Prefer not to answer')),
        initial=False,
        widget=forms.RadioSelect
    )

    """
    #should I change this to birthday? - yes
        #under_age
        under_age = forms.IntegerField(
            required=True,
            label='What is your birth date?',
        )
    """
    # UGAHacks Newsletter
    hacks_newsletter = forms.BooleanField(
        required=False,
        label='I authorize UGAHacks to send me updates about the organization and promotional material about future events as a digital newsletter to the email associated with this account.'
    )

    # MLH Code of Conduct
    code_of_conduct = forms.BooleanField(
        required=True,
        label='I have read and agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf" target="_blank">MLH Code of Conduct</a>, the <a href="https://github.com/MLH/mlh-policies/blob/master/prize-terms-and-conditions/contest-terms.md" target="_blank">MLH Contest Terms and Conditions</a>, and the <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>.<span style="color: red; font-weight: bold;"> *</span>'
    )

    # MLH Terms and Conditions
    terms_and_conditions = forms.BooleanField(
        required=True,
        label='I authorize you to share my application/registration information for event administration, ranking, MLH administration, and for MLH to send pre- and post-event informational e-mails/occasional messages about hackathons all in accordance with the <a href="https://mlh.io/privacy" target="_blank">MLH Privacy Policy</a>.<span style="color: red; font-weight: bold;"> *</span>'
    )

    cvs_edition = forms.BooleanField(
        required=True,
        label='I have read and agree to the above UGAHacks policies upon submitting my application.<span style="color: red; font-weight: bold;"> *</span>'
    )

    diet_notice = forms.BooleanField(
        required=False,
        label='I authorize "UGAHacks" to use my food allergies and intolerances information to '
              'manage the catering service only.<span style="color: red; font-weight: bold;"> *</span>'
    )

    resume = forms.FileField(required=False)

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        size = getattr(resume, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep resume size under %s. Current filesize %s!" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return resume

    def clean_terms_and_conditions(self):
        terms = self.cleaned_data.get('terms_and_conditions', False)
        if not terms:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept MLH's Terms & Conditions and"
                " Privacy Policy."
            )
        return terms

    def clean_code_of_conduct(self):
        code = self.cleaned_data.get('code_of_conduct', False)
        if not code:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept MLH's Code of Conduct."
            )
        return code

    def clean_cvs_edition(self):
        cc = self.cleaned_data.get('cvs_edition', False)
        return cc

    def clean_diet_notice(self):
        diet = self.cleaned_data['diet']
        diet_notice = self.cleaned_data.get('diet_notice', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if diet != 'None' and not diet_notice:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept us to use your personal data related to your food "
                "allergies and intolerances only in order to manage the catering service."
            )
        return diet_notice

    def clean_github(self):
        data = self.cleaned_data['github']
        validate_url(data, 'github.com')
        return data

    def clean_devpost(self):
        data = self.cleaned_data['devpost']
        validate_url(data, 'devpost.com')
        return data

    def clean_linkedin(self):
        data = self.cleaned_data['linkedin']
        validate_url(data, 'linkedin.com')
        return data

    def clean_projects(self):
        data = self.cleaned_data['projects']
        if not data:
            raise forms.ValidationError("Please fill this in order for us to know you a bit better.")
        return data

    # def clean_reimb_amount(self):
    #     data = self.cleaned_data['reimb_amount']
    #     reimb = self.cleaned_data.get('reimb', False)
    #     if reimb and not data:
    #         raise forms.ValidationError("To apply for reimbursement please set a valid amount.")
    #     deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
    #     if data and deadline and deadline <= timezone.now():
    #         raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
    #     return data

    def clean_reimb(self):
        reimb = self.cleaned_data.get('reimb', False)
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        if reimb and deadline and deadline <= timezone.now():
            raise forms.ValidationError("Reimbursement applications are now closed. Trying to hack us?")
        return reimb

    def clean_volunteer_time(self):
        data = self.cleaned_data['volunteer_time']
        return data

    def clean_mentor_topic(self):
        data = self.cleaned_data['mentor_topic']
        return data

    def clean_mentor_workshop(self):
        data = self.cleaned_data['mentor_workshop']
        return data

    def clean_other_diet(self):
        data = self.cleaned_data['other_diet']
        diet = self.cleaned_data['diet']
        if diet == 'Others' and not data:
            raise forms.ValidationError("Please tell us your specific dietary requirements")
        return data

    def clean_uniemail(self):
        data = self.cleaned_data['uniemail']
        return data

    #    def clean_other_gender(self):
    #        data = self.cleaned_data['other_gender']
    #        gender = self.cleaned_data['gender']
    #        if gender == models.GENDER_OTHER and not data:
    #            raise forms.ValidationError("Please enter this field or select 'Prefer not to answer'")
    #        return data

    def clean(self):
        cleaned_data = super().clean()
        participant = cleaned_data.get('participant')

        volunteer_time = cleaned_data.get('volunteer_time')
        if participant == 'Volunteer' and not volunteer_time:
            raise forms.ValidationError("Please tell us what time you want to volunteer")

        mentor_topic = cleaned_data.get('mentor_topic')
        if participant == 'Mentor' and not mentor_topic:
            raise forms.ValidationError("Please tell us what topic you want to mentor for")

        mentor_workshop = cleaned_data.get('mentor_workshop')
        if participant == 'Mentor' and not mentor_workshop:
            raise forms.ValidationError("Please tell us if you would like to host a workshop")

        uniemail = cleaned_data.get('uniemail')
        if uniemail:
            if (participant == 'Hacker' or participant == 'Volunteer') and '.edu' not in uniemail:
                raise forms.ValidationError("Please enter your school email")
        else:
            if participant == 'Mentor':
                uniemail = 'byte@uga.edu'
            else:
                raise forms.ValidationError("Please enter your school email")

    def __getitem__(self, name):
        item = super(ApplicationForm, self).__getitem__(name)
        item.field.disabled = not self.instance.can_be_edit()
        return item

    def fieldsets(self):
        # Fieldsets ordered and with description
        self._fieldsets = [
            ('Personal Info',
             {'fields': ('participant', 'volunteer_time', 'mentor_topic', 'mentor_workshop', 'university', 'degree',
                         'class_status', 'graduation_year', 'uniemail', 'gender', 'other_gender', 'ethnicity',
                         'phone_number', 'tshirt_size', 'diet', 'other_diet'),
              'description': 'Hey there, thank you for your interest in attending UGAHacks. To begin, we would like to know a little more about you.', }),
            ('Hackathons?', {'fields': ('description', 'first_timer', 'first_ugahacks', 'hearabout', 'projects', 'hardware'), }),
            ('Show us what you\'ve built',
             {'fields': ('github', 'devpost', 'linkedin', 'site', 'resume'),
              'description': 'Some of our sponsors may use this information for recruitment purposes,'
                             ' so please include as much as you can.'}),
        ]
        deadline = getattr(settings, 'REIMBURSEMENT_DEADLINE', False)
        r_enabled = getattr(settings, 'REIMBURSEMENT_ENABLED', False)
        if r_enabled and deadline and deadline <= timezone.now() and not self.instance.pk:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',),
                                     'description': 'Reimbursement applications are now closed. '
                                                    'Sorry for the inconvenience.',
                                     }))
        elif self.instance.pk and r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',),
                                     'description': 'If you applied for reimbursement, we will reach out to you about fulfilling your reimbursement during the event. '
                                                    'Email us at %s for any change needed on reimbursements.' %
                                                    settings.HACKATHON_CONTACT_EMAIL,
                                     }))
        elif not r_enabled:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin',)}), )
        else:
            self._fieldsets.append(('Traveling',
                                    {'fields': ('origin', 'reimb'), }), )

        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        digital_hack_enabled = getattr(settings, 'DIGITAL_HACKATHON', False)
        if digital_hack_enabled:
            self._fieldsets.append(('Shipping Address', {
                'fields': ('address','city','state','zip_code'),
                'description': '<p style="color: #202326cc;margin-top: 1em;display: block;'
                               'margin-bottom: 1em;line-height: 1.25em;">Due to Covid-19, there is a likelihood that our upcoming event, UGAHacks 6, will be digital. '
                               'If that ends up being the case, we would still want to be able to ship prizes and swag to as many of our participants as possible (as deemed reasonable given shipping costs). '
                               'Thus, we are asking applicants to voluntarily submit their shipping address to assist with logistics. The addresses submitted will solely be used to send prizes/swag and will be '
                               'deleted after the event or as per hacker request to hello@ugahacks.com.</p>'
            }))

        # this if statement gave a bug when the user tried to update their application
        # if not self.instance.pk:
        self._fieldsets.append(('UGAHacks Policies', {
            'fields': ('cvs_edition', 'hacks_newsletter', 'terms_and_conditions', 'code_of_conduct', 'diet_notice'),
            'description': '<p style="color: #202326cc;margin-top: 1em;display: block;'
                           'margin-bottom: 1em;line-height: 1.25em;">We, UGAHacks, '
                           'will be processing your information with the aim of giving you and others the best possible experience. '
                           'By submitting an application, your data will be used according to the following <a href="https://www.ugahacks.com/privacy" target="_blank">Privacy Policy</a>, which includes sharing information such as resumes with our Sponsors. '
                           'You are also agreeing to the terms in the <a href="url legal_notice" target="_blank">Liability Release, Covenant Not to Sue, and Ownership Agreement</a> in order to participate in the event. '
                           'Finally, you are also authorizing us to the use of any images and videos of yourself during the event.</p>'
        }))
        return super(ApplicationForm, self).fieldsets

    class Meta:
        model = models.Application
        help_texts = {
            'participant': 'Volunteers will still be able to participate in the hackathon and submit projects',
            'volunteer_time': 'What time(s) can you volunteer? (Please give date and time ranges if possible)',
            'mentor_topic': 'What topics are you confortable mentoring in?',
            'mentor_workshop': 'Are you interested in hosting a workshop? If so, please describe what you would like to host.',
            'gender': 'This is for demographic purposes. You can skip this question if you want.',
            'hearabout': "This is for marketing purposes. You can skip this question if you want.",
            'class_status': 'Base your response on the number of years of college you have completed not credit hours.',
            'graduation_year': 'What year have you graduated on or when will you graduate?',
            'uniemail': 'This will be used to verify that you are a student.',
            'degree': 'What\'s your major/degree?',
            'other_diet': 'Please fill here in your dietary requirements. We want to make sure we have food for you!',
            'hardware': 'Any hardware that you would like us to have. We can\'t promise anything, '
                        'but at least we\'ll try!',
            'projects': 'You can talk about about past hackathons, personal projects, awards etc. '
                        '(we love links) Show us your passion! :D',
        }

        widgets = {
            'origin': forms.TextInput(attrs={'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'projects': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'graduation_year': forms.RadioSelect(),
            'class_status': forms.RadioSelect(),
        }

        labels = {
            'participant': 'What type of participant are you?',
            'gender': 'What gender do you identify as?',
            'other_gender': 'Self-describe',
            'class_status': 'What is your class status?',
            'graduation_year': 'What year will you graduate?',
            'uniemail': 'What is your university/school email (.edu)?',
            'tshirt_size': 'What\'s your t-shirt size?',
            'diet': 'Dietary requirements',
            'hardware': 'Hardware you would like us to have',
            'origin': 'What city are you joining us from?',
            'hearabout': 'How did you hear about %s?' % settings.HACKATHON_NAME,
            'description': 'Why are you excited about %s?' % settings.HACKATHON_NAME,
            'projects': 'What projects have you worked on? How do you see yourself building the future?',
            'resume': 'Upload your resume',
            'state': 'State/Province'
        }

        exclude = ['user', 'uuid', 'invited_by', 'submission_date', 'status_update_date', 'status', ]
