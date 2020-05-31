from django.contrib import admin

from sponsors import models

# Register your models here.
admin.site.register(models.SponsorApplication)
admin.site.register(models.Sponsor)
