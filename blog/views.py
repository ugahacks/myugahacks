from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import BlogAddForm
from datetime import datetime
from .models import Blog
from user.mixins import IsOrganizerMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import queue
from collections import OrderedDict

class BlogAdd(IsOrganizerMixin, CreateView):
    template_name = 'blog_add.html'
    success_url = '/'
    form_class = BlogAddForm
    model = Blog

    def form_valid(self, form):
        blog = form.save(commit=False)
        blog.publication_date = datetime.now()
        blog.author = self.request.user
        blog.save()
        form.save_m2m()
        return super(BlogAdd, self).form_valid(form)

'''
class BlogAdd(IsOrganizerMixin, FormView):
    template_name = 'blog_add.html'
    success_url = ''
    form_class = BlogAddForm

    def form_valid(self, form):
        blog = form.save(commit=False)
        blog.publication_date = datetime.now()
        blog.author = self.request.user
        blog.save()
        form.save_m2m()
        return super(BlogAdd, self).form_valid(form)
'''

class BlogEdit(IsOrganizerMixin, UpdateView):
    model = Blog
    success_url = '/'
    form_class = BlogAddForm
    template_name = 'blog_edit.html'

    def get_context_data(self, **kwargs):
        context = super(BlogEdit, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        blog = form.save(commit=False)
        blog.publication_date = datetime.now()
        blog.save()
        form.save_m2m()
        return super(BlogEdit, self).form_valid(form)

class BlogHome(ListView):
    template_name = 'blog_home.html'
    model = Blog
    paginate_by = 10
    ordering = ['-publication_date']
    context_object_name = 'blogs'

    def get_queryset(self):
        blog_query = Blog.objects.all().order_by('-publication_date')
        keywords = self.request.GET.get('blog-search')
        if keywords:
            search_queue = queue.PriorityQueue()
            keywords = keywords.lower()
            for blog in blog_query:
                if keywords in blog.title.lower():
                    search_queue.put((1, blog))
                if keywords in [str(tag).lower() for tag in blog.tags.all()]:
                    search_queue.put((2, blog))
                if keywords in blog.description.lower():
                    search_queue.put((3, blog))
                if keywords in blog.content.lower():
                    search_queue.put((4, blog))
            blog_query = [blog[1] for blog in search_queue.queue]
            #This is used to make the list distinct while preserving order.
            blog_query = list(OrderedDict.fromkeys(blog_query))
            return blog_query
        return blog_query


class BlogDetail(DetailView):
    model = Blog
    template_name = 'blog_detail.html'
