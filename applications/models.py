from __future__ import unicode_literals

import json

import uuid as uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from app import utils
from user.models import User


class Application(models.Model):
    PENDING = 'P'
    REJECTED = 'R'
    INVITED = 'I'
    LAST_REMINDER = 'LR'
    CONFIRMED = 'C'
    CANCELLED = 'X'
    ATTENDED = 'A'
    EXPIRED = 'E'
    DUBIOUS = 'D'

    STATUS = [
        (PENDING, 'Under review'),
        (REJECTED, 'Wait listed'),
        (INVITED, 'Invited'),
        (LAST_REMINDER, 'Last reminder'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
        (ATTENDED, 'Attended'),
        (EXPIRED, 'Expired'),
        (DUBIOUS, 'Dubious')
    ]

    NO_ANSWER = 'NA'
    MALE = 'M'
    FEMALE = 'F'
    NON_BINARY = 'NB'

    GENDERS = [
        (NO_ANSWER, 'Prefer not to answer'),
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NON_BINARY, 'Non-binary'),
    ]

    D_NONE = 'None'
    D_VEGETARIAN = 'Vegetarian'
    D_VEGAN = 'Vegan'
    D_HALAL = 'Halal'
    D_KOSHER = 'Kosher'
    D_GLUTEN_FREE = 'Gluten-free'
    D_NO_PORK = 'No pork'
    D_NO_PEANUTS = 'No peanuts/nuts'
    D_NO_DAIRY = 'No dairy'
    D_OTHER = 'Others'

    DIETS = [
        (D_NONE, 'None'),
        (D_VEGETARIAN, 'Vegetarian'),
        (D_VEGAN, 'Vegan'),
        (D_HALAL, 'Halal'),
        (D_KOSHER, 'Kosher'),
        (D_GLUTEN_FREE, 'Gluten-free'),
        (D_NO_PORK, 'No pork'),
        (D_NO_PEANUTS, 'No peanuts/nuts'),
        (D_NO_DAIRY, 'No dairy'),
        (D_OTHER, 'Others')
    ]

    P_HACKER = 'Hacker'
    P_VOLUNTEER = 'Volunteer'
    P_MENTOR = 'Mentor'

    PARTICIPANTS = [
        (P_HACKER, 'Hacker'),
        (P_VOLUNTEER, 'Volunteer'),
        (P_MENTOR, 'Mentor'),
    ]

    A_VIRTUAL = 'Virtual'
    A_PHYSICAL = 'In-person'

    ATTENDANCE = [
        (A_VIRTUAL, 'Virtual'),
        (A_PHYSICAL, 'In-person'),
    ]

    T_XXS = 'XXS'
    T_XS = 'XS'
    T_S = 'S'
    T_M = 'M'
    T_L = 'L'
    T_XL = 'XL'
    T_XXL = 'XXL'

    TSHIRT_SIZES = [
        (T_XXS, "Unisex - XXS"),
        (T_XS, "Unisex - XS"),
        (T_S, "Unisex - S"),
        (T_M, "Unisex - M"),
        (T_L, "Unisex - L"),
        (T_XL, "Unisex - XL"),
        (T_XXL, "Unisex - XXL"),
    ]
    DEFAULT_TSHIRT_SIZE = T_M

    YEARS = [(int(size), size) for size in ('2020 2021 2022 2023 2024'.split(' '))]
    DEFAULT_YEAR = 2020

    C_FRESHMAN = 'Freshman'
    C_SOPHOMORE = 'Sophomore'
    C_JUNIOR = 'Junior'
    C_SENIOR = 'Senior'
    C_GRAD = 'Graduate Student'
    C_GRADUATED = 'Graduated'

    CLASSSTATUS = [
        (C_FRESHMAN, 'Freshman'),
        (C_SOPHOMORE, 'Sophomore'),
        (C_JUNIOR, 'Junior'),
        (C_SENIOR, 'Senior'),
        (C_GRAD, 'Graduate Student'),
        (C_GRADUATED, 'Graduated')
    ]

    H_NOANS = "N/A"
    H_SEARCH = 'Search Engine'
    H_TWITTER = 'Twitter'
    H_FACEBOOK = 'Facebook'
    H_INSTAGRAM = 'Instagram'
    H_GITHUB = 'GitHub'
    H_EMAIL = "Promotional Emails"
    H_FRIENDS = "Friends"
    H_PROF = "Professors/University-wide announcement"
    H_MLH = "MLH Website"

    HEARABOUT = [
        (H_NOANS, "N/A"),
        (H_SEARCH, 'Search Engine'),
        (H_TWITTER, 'Twitter'),
        (H_FACEBOOK, 'Facebook'),
        (H_INSTAGRAM, 'Instagram'),
        (H_GITHUB, 'Github'),
        (H_EMAIL, 'Promotional Emails'),
        (H_FRIENDS, 'Friends'),
        (H_PROF, 'Professors/University-wide announcement'),
        (H_MLH, 'MLH Website'),
    ]

    # META
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, related_name='invited_applications', blank=True, null=True,
                                   on_delete=models.CASCADE)
    contacted = models.BooleanField(default=False)  # If a dubious application has been contacted yet
    contacted_by = models.ForeignKey(User, related_name='contacted_by', blank=True, null=True,
                                     on_delete=models.CASCADE)

    # When was the application submitted
    submission_date = models.DateTimeField(default=timezone.now)
    # When was the last status update
    status_update_date = models.DateTimeField(blank=True, null=True)
    # Application status
    status = models.CharField(choices=STATUS, default=PENDING,
                              max_length=2)

    # managers
    objects = models.Manager()

    # ABOUT YOU
    # Population analysis, optional
    gender = models.CharField(max_length=23, choices=GENDERS, default=NO_ANSWER)
    other_gender = models.CharField(max_length=50, blank=True, null=True)
    ethnicity = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=14,
                                    validators=[RegexValidator(regex=r'^\(\d{3}\)\s\d{3}-\d{4}',
                                                               message="Phone number must be entered in the following format: \
                                                                (999) 999-9999")],
                                    default='(999) 999-9999')

    """
        # Personal data (asking here because we don't want to ask birthday)
        birth_year = models.IntegerField(null=True)
    """
    uniemail = models.EmailField(verbose_name='university_email', max_length=255, unique=True, blank=True, null=True)
    # Where is this person coming from?
    origin = models.CharField(max_length=300)

    # Is this your first hackathon?
    first_timer = models.BooleanField()
    first_ugahacks = models.BooleanField()
    # Why do you want to come to X?
    description = models.TextField(max_length=500)
    hearabout = models.CharField(max_length=50, choices=HEARABOUT, default=H_NOANS)
    # Explain a little bit what projects have you done lately
    projects = models.TextField(max_length=500, blank=True, null=True)

    # Reimbursement
    reimb = models.BooleanField(default=False)
    reimb_amount = models.FloatField(blank=True, null=True, validators=[
        MinValueValidator(0, "Negative? Really? Please put a positive value")])

    # Participant
    attendance_type = models.CharField(max_length=300, choices=ATTENDANCE, default=A_VIRTUAL)
    participant = models.CharField(max_length=300, choices=PARTICIPANTS, default=P_HACKER)
    volunteer_time = models.CharField(max_length=600, blank=True, null=True)
    mentor_topic = models.CharField(max_length=600, blank=True, null=True)
    mentor_workshop = models.CharField(max_length=600, blank=True, null=True)

    # Giv me a resume here!
    resume = models.FileField(upload_to='resumes', null=True, blank=True)
    cvs_edition = models.BooleanField(default=False)
    code_of_conduct = models.BooleanField(default=False)
    terms_and_conditions = models.BooleanField(default=False)
    hacks_newsletter = models.BooleanField(default=False)
    MLH_promotional = models.BooleanField(default=False)

    # University
    graduation_year = models.IntegerField(choices=YEARS, default=DEFAULT_YEAR)
    class_status = models.CharField(max_length=300, choices=CLASSSTATUS, default=C_FRESHMAN)
    university = models.CharField(max_length=300)
    degree = models.CharField(max_length=300)

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    # Info for swag and food
    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)
    tshirt_size = models.CharField(max_length=5, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)

    # Info for hardware
    hardware = models.CharField(max_length=300, null=True, blank=True)

    # Shipping Address for Prizes
    address_line = models.CharField(max_length=300, null=True, blank=True)
    address_line_2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)

    @classmethod
    def annotate_vote(cls, qs):
        return qs.annotate(vote_avg=Avg('vote__calculated_vote'))

    @property
    def uuid_str(self):
        return str(self.uuid)

    def get_soft_status_display(self):
        text = self.get_status_display()
        if "Not" in text or 'Rejected' in text:
            return "Pending"
        return text

    def __str__(self):
        return self.user.email

    def save(self, **kwargs):
        self.status_update_date = timezone.now()
        super(Application, self).save(**kwargs)

    def invite(self, user):
        # We can't re-invite someone invited
        if self.status in [self.CONFIRMED, self.ATTENDED]:
            raise ValidationError('Application has already answered invite. '
                                  'Current status: %s' % self.status)
        if not self.invited_by:
            self.invited_by = user
        self.last_invite = timezone.now()
        self.last_reminder = None
        self.__set_status(self.INVITED)

    def last_reminder(self):
        if self.status != self.INVITED:
            raise ValidationError('Reminder can\'t be sent to non-pending '
                                  'applications')
        self.__set_status(self.LAST_REMINDER)

    def expire(self):
        self.__set_status(self.EXPIRED)

    def reject(self, request):
        if self.status == self.ATTENDED:
            raise ValidationError('Application has already attended. '
                                  'Current status: %s' % self.status)
        self.__set_status(self.REJECTED)

    def confirm(self):
        if self.status == self.CANCELLED:
            raise ValidationError('This invite has been cancelled.')
        elif self.status == self.EXPIRED:
            raise ValidationError('Unfortunately your invite has expired.')
        elif self.status in [self.INVITED, self.LAST_REMINDER]:
            self.__set_status(self.CONFIRMED)
        elif self.status in [self.CONFIRMED, self.ATTENDED]:
            return None
        else:
            raise ValidationError('Unfortunately his application hasn\'t been '
                                  'invited [yet]')

    def cancel(self):
        if not self.can_be_cancelled():
            raise ValidationError('Application can\'t be cancelled. Current '
                                  'status: %s' % self.status)
        if self.status != self.CANCELLED:
            self.__set_status(self.CANCELLED)
            reimb = getattr(self.user, 'reimbursement', None)
            if reimb:
                reimb.delete()

    def check_in(self):
        self.__set_status(self.ATTENDED)

    def set_dubious(self):
        self.__set_status(self.DUBIOUS)
        self.contacted = False

    def unset_dubious(self):
        self.__set_status(self.PENDING)

    def set_contacted(self, user):
        if not self.contacted:
            self.contacted = True
            self.contacted_by = user
            self.save()

    # Private
    def __set_status(self, status):
        self.status = status
        self.save()

    def is_confirmed(self):
        return self.status == self.CONFIRMED

    def is_cancelled(self):
        return self.status == self.CANCELLED

    def answered_invite(self):
        return self.status in [self.CONFIRMED, self.CANCELLED, self.ATTENDED]

    def needs_action(self):
        return self.status == self.INVITED

    def is_pending(self):
        return self.status == self.PENDING

    def can_be_edit(self):
        return self.status == self.PENDING and not self.vote_set.exists() and not utils.is_app_closed()

    def is_invited(self):
        return self.status == self.INVITED

    def is_expired(self):
        return self.status == self.EXPIRED

    def is_rejected(self):
        return self.status == self.REJECTED

    def is_attended(self):
        return self.status == self.ATTENDED

    def is_last_reminder(self):
        return self.status == self.LAST_REMINDER

    def is_dubious(self):
        return self.status == self.DUBIOUS

    def can_be_cancelled(self):
        return self.status in [self.CONFIRMED, self.INVITED, self.LAST_REMINDER]

    def can_confirm(self):
        return self.status in [self.INVITED, self.LAST_REMINDER]

    def serialize(self):
        return {
            'user': {
                'name': self.user.name,
                'email': self.user.email,
                'is': {
                    'active': self.user.is_active,
                    'volunteer': self.user.is_volunteer,
                    'organizer': self.user.is_organizer,
                    'director': self.user.is_director,
                    'sponsor': self.user.is_sponsor,
                    'admin': self.user.is_admin,
                    'mentor': self.user.is_mentor,
                    'hardwareAdmin': self.user.is_hardware_admin,
                },
                'application': {
                    # Info for swag and food
                    'diet': self.diet,
                    'otherDiet': self.other_diet,
                    'tshirtSize': self.tshirt_size,
                    # Info for hardware
                    'hardware': self.hardware,
                }
            }
        }


class DraftApplication(models.Model):
    content = models.CharField(max_length=7000)
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)

    def save_dict(self, d):
        self.content = json.dumps(d)

    def get_dict(self):
        return json.loads(self.content)
