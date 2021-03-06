from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class SponsorApplication(models.Model):
    from applications.models import Application
    # String of user.User to prevent circular dependecies
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)

    tshirt_size = models.CharField(max_length=5, choices=Application.TSHIRT_SIZES)

    diet = models.CharField(max_length=300, choices=Application.DIETS, default=Application.D_NONE)

    other_diet = models.CharField(max_length=600, blank=True, null=True)

    company_logo = models.ImageField(upload_to='sponsor_logos', null=True, blank=True)

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
                    'diet': self.diet,
                    'otherDiet': self.other_diet,
                    'tshirtSize': self.tshirt_size,
                }
            }
        }


class Sponsor(models.Model):
    # Sponsor Tiers
    C_TIER_1 = 'Tier1'
    C_TIER_2 = 'Tier2'
    C_TIER_3 = 'Tier3'
    C_COHOST = 'Co-Host'

    # Tier choices used for the database. Right hand of tuple is just for semantics.
    TIERS = [
        (C_TIER_1, 'Doghouse'),
        (C_TIER_2, 'Apartment'),
        (C_TIER_3, 'Penthouse'),
        (C_COHOST, 'Mansion'),
    ]

    C_TIER_1_POINTS = 3
    C_TIER_2_POINTS = 5
    C_TIER_3_POINTS = 7
    C_COHOST_POINTS = 10

    company = models.CharField(max_length=255, unique=True)

    email_domain = models.CharField(max_length=255, unique=True)

    tier = models.CharField(max_length=255, choices=TIERS)

    scanned_hackers = models.ManyToManyField('user.User')

    def get_tier_value(self):
        if self.tier == self.C_TIER_1:
            return self.C_TIER_1_POINTS
        elif self.tier == self.C_TIER_2:
            return self.C_TIER_2_POINTS
        elif self.tier == self.C_TIER_3:
            return self.C_TIER_3_POINTS
        elif self.tier == Sponsor.C_COHOST:
            return self.C_COHOST_POINTS
