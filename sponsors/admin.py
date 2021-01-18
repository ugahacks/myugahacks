from django.contrib import admin
from sponsors import models

# Register your models here.

class SponsorApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tshirt_size', 'diet')
    search_fields = ('user__email',)

class SponsorAdmin(admin.ModelAdmin):
    list_display = ('company', 'email_domain', 'tier')
    search_fields = ('company',)

admin.site.register(models.SponsorApplication, admin_class=SponsorApplicationAdmin)
admin.site.register(models.Sponsor, admin_class=SponsorAdmin)
