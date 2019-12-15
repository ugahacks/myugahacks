from django.contrib import admin
from workshops import models


# Register your models here.

admin.site.register(models.Workshop)

admin.site.register(models.Timeslot)
