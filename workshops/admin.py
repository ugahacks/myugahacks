from django.contrib import admin
from workshops import models

class WorkshopsWorkshopAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'location', 'host', 'opened', 'starts', 'ends'
    )
    search_fields = (
        'name',
    )

    def get_actions(self, request):
        return []


class WorkshopsAttendedAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'workshop', 'user', 'time'
    )
    search_fields = (
        'name', 'user__name', 'user__email'
    )
    list_filter = (
        'workshop', 'user'
    )

    def get_actions(self, request):
        return []


admin.site.register(models.Workshop, admin_class=WorkshopsWorkshopAdmin)
admin.site.register(models.Attended, admin_class=WorkshopsAttendedAdmin)
