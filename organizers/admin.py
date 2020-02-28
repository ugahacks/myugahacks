from django.contrib import admin

# Register your models here.
from organizers import models


class OrganizerBaseAdmin(admin.ModelAdmin):
    list_display = ()
    list_per_page= 200
    list_filter = ()
    search_fields = ()
    #actions = ['delete_selected']


class CommentAdmin(OrganizerBaseAdmin):
    list_display = OrganizerBaseAdmin.list_display + ('application', 'author', 'text')
    #list_per_page = 200
    date_hierarchy = 'created_at'



class VoteAdmin(OrganizerBaseAdmin):
    list_display = OrganizerBaseAdmin.list_display + ('application', 'user', 'tech', 'personal', 'calculated_vote')
    #list_per_page = 200
    list_filter = OrganizerBaseAdmin.list_filter + ('user', 'application')
    search_fields = OrganizerBaseAdmin.search_fields + ('user', 'application')



admin.site.register(models.ApplicationComment, admin_class=CommentAdmin)
admin.site.register(models.Vote, admin_class=VoteAdmin)
