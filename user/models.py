from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, **kwargs):
        if not email:
            raise ValueError('Users must have a email')
        name = kwargs.pop('name', '')
        if name:
            user = self.model(
                email=email,
                name=name
            )
            password = kwargs.pop('password', '')
            user.set_password(password)
        else:
            if len(User.objects.filter(email=email)) == 0:
                first_name = kwargs.pop('first_name','')
                last_name = kwargs.pop('last_name','')
                user = self.model(
                    email=email,
                    name=str(first_name + ' ' + last_name)
                )
                user.set_unusable_password()
                user.email_verified = True
            else:
                return User.objects.get(email=email)

        user.save(using=self._db)
        return user

    def create_mlhuser(self, email, name, mlh_id):
        if not email:
            raise ValueError('Users must have a email')
        if not mlh_id:
            raise ValueError('Users must have a mlh id')

        user = self.model(
            email=email,
            name=name,
            mlh_id=mlh_id
        )
        user.set_unusable_password()
        user.email_verified = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.is_director = True
        user.is_organizer = True
        user.is_admin = True
        user.email_verified = True
        user.is_volunteer = True
        user.is_hardware_admin = True
        user.save(using=self._db)
        return user


class Role(models.Model):

    title = models.CharField(max_length=63, null=False)

    description = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.title


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        verbose_name='Full name',
        max_length=255,
    )
    email_verified = models.BooleanField(default=False)

    profile_picture = models.ImageField(upload_to='user/profile_pictures',
                                        default='user/profile_pictures/default_profile_picture.jpg')

    role = models.ForeignKey(Role, on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_volunteer = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_sponsor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    is_hardware_admin = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now)
    mlh_id = models.IntegerField(blank=True, null=True, unique=True)
    on_duty = models.BooleanField(default=False)
    duty_update_time = models.DateTimeField(null=True, verbose_name="Last Checked In")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def get_full_name(self):
        # The user is identified by their nickname/full_name address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_tier_value(self):
        from sponsors.models import Sponsor
        # Admin's will default to TIER_1 if debug is on
        if self.is_admin and settings.DEBUG:
            return Sponsor.C_TIER_1_POINTS
        if not self.is_sponsor:
            return None
        domain = self.email.split('@')[1]
        sponsor = Sponsor.objects.filter(email_domain=domain)
        return sponsor.get_tier_value()

    # Used by django auth. Please do not remove.
    @property
    def is_superuser(self):
        return self.is_admin

    # Use this one throughout the app for semantic clarity
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
