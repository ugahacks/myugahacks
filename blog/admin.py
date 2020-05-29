from django.contrib import admin
from blog import models


# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','author','publication_date')
    search_fields = ('title','author__name')

admin.site.register(models.Blog, admin_class=BlogAdmin)
