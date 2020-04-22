from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django_filters.views import FilterView
from .forms import BlogAddForm
from datetime import datetime
from .models import Blog, Tag
from user.mixins import IsOrganizerMixin
from app.mixins import TabsViewMixin
from django_tables2 import SingleTableMixin
from blog.tables import BlogPostsListTable, BlogPostsListFilter

class BlogAdd(FormView):
    template_name = 'blog_add.html'
    success_url = '#'
    form_class = BlogAddForm

    def form_valid(self, form):
        blog = form.save(commit=False)
        tags = form.cleaned_data['tags'].split(',')
        blog.publication_date = datetime.now()
        blog.author = self.request.user
        blog.save()
        for tag in tags:
            tag = Tag(blog=blog, tag=tag.strip())
            tag.save()
        return super().form_valid(form)

class BlogHome(ListView):
    template_name = 'blog_home.html'
    model = Blog
    context_object_name = 'blogs'
    paginate_by = 10

class BlogPostList(IsOrganizerMixin, TabsViewMixin, SingleTableMixin, FilterView):
    template_name = 'blog_list.html'
    table_class = BlogPostsListTable
    filterset_class = BlogPostsListFilter
    table_pagination = {'per_page': 20}
