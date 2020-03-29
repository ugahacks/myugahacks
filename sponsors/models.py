from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

D_NONE = 'None'
D_VEGETERIAN = 'Vegeterian'
D_VEGAN = 'Vegan'
D_NO_PORK = 'No pork'
D_GLUTEN_FREE = 'Gluten-free'
D_OTHER = 'Others'

DIETS = [
    (D_NONE, 'No requirements'),
    (D_VEGETERIAN, 'Vegeterian'),
    (D_VEGAN, 'Vegan'),
    (D_NO_PORK, 'No pork'),
    (D_GLUTEN_FREE, 'Gluten-free'),
    (D_OTHER, 'Others')
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

#List as Tier rather than the Tier name so it is easy to change in the future.
C_TIER_1 = 'Tier 1'
C_TIER_2 = 'Tier 2'
C_TIER_3 = 'Tier 3'
C_COHOST = 'Co-Host'

#Change the Tier names here.
TIERS = [
    (C_TIER_1, 'Doghouse'),
    (C_TIER_2, 'Apartment'),
    (C_TIER_3, 'Penthouse'),
    (C_COHOST, 'Mansion'),
]


class SponsorApplication(AbstractBaseUser):
    #String of user.User to prevent circular dependecies
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)

    tshirt_size = models.CharField(max_length=5, choices=TSHIRT_SIZES)

    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)

    other_diet = models.CharField(max_length=600, blank=True, null=True)

    company_logo = models.ImageField(upload_to = 'sponsor_logos', null=True, blank=True)

class Sponsor(models.Model):
    company = models.CharField(max_length=255)

    email_domain = models.CharField(max_length=255)

    tier = models.CharField(max_length=255, choices=TIERS)
