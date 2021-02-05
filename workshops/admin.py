from django.contrib import admin

from workshops import models

# Register your models here.

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('workshop', 'user')
    search_fields = ('workshop', 'user__name', 'user__email')
    list_filter = ('workshop',)

    def get_actions(self, request):
        return []

admin.site.register(models.Attendance, admin_class=AttendanceAdmin)

admin.site.register(models.Workshop)

admin.site.register(models.Timeslot)
