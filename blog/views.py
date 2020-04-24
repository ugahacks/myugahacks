from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import BlogAddForm
from datetime import datetime
from .models import Blog, Tag

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
    paginate_by = 10
    context_object_name = 'blogs'

class BlogDetail(DetailView):
    model = Blog
    template_name = 'blog_detail.html'
