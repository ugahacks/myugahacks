from django.contrib import admin

from scanning import models


# Register your models here.

class ScanningAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'application', 'update_time'
    )
    search_fields = list_display
    date_hierarchy = 'update_time'

    def get_actions(self, request):
        return []


admin.site.register(models.Scanning, admin_class=ScanningAdmin)
