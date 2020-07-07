from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from app.mixins import TabsViewMixin
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from blog.models import Blog
from blogadmin.tables import BlogAdminTable, BlogAdminFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
from user.mixins import IsDirectorMixin

# Create your views here.
class BlogAdminHome(IsDirectorMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'blog_admin_home.html'
    table_class = BlogAdminTable
    table_pagination = {'per_page': 100}
    filterset_class = BlogAdminFilter


class BlogAdminDetail(IsDirectorMixin, DetailView):
    model = Blog
    template_name = 'blog_admin_detail.html'

class BlogAdminApprove(IsDirectorMixin, View):
    def get(self, request, blog_id):
        approved_blog = Blog.objects.get(id=blog_id)
        approved_blog.approved = not approved_blog.approved
        approved_blog.save()
        return HttpResponseRedirect(reverse('blogadmin:blog_admin_home'))
