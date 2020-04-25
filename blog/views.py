from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import BlogAddForm, BlogEditForm
from datetime import datetime
from .models import Blog, Tag
from user.mixins import IsOrganizerMixin

class BlogAdd(FormView):
    template_name = 'blog_add.html'
    success_url = '/blog/'
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

class BlogEdit(IsOrganizerMixin, UpdateView):
    model = Blog
    success_url = '/blog/'
    form_class = BlogEditForm
    template_name = 'blog_edit.html'

    def get_context_data(self, **kwargs):
        context = super(BlogEdit, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        blog = form.save(commit=False)
        tags = form.cleaned_data['tags'].split(',')
        blog.publication_date = datetime.now()
        blog.save()
        for tag in tags:
            tag = Tag(blog=blog, tag=tag.strip())
            tag.save()
        return super(BlogEdit, self).form_valid(form)

class BlogHome(ListView):
    template_name = 'blog_home.html'
    model = Blog
    paginate_by = 10
    ordering = ['-publication_date']
    context_object_name = 'blogs'

class BlogDetail(DetailView):
    model = Blog
    template_name = 'blog_detail.html'
