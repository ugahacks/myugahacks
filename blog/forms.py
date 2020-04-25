from django import forms
from .models import Blog
from froala_editor.widgets import FroalaEditor

class BlogAddForm(forms.ModelForm):
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256, help_text='Briefly describe the content of your blog post (This will appear when looking at the list of blog posts).')
    tags = forms.CharField(help_text='Enter tags seperated by commas.')
    thumbnail = forms.ImageField()
    content = forms.CharField(widget=FroalaEditor)

    class Meta:
        model = Blog
        fields = ['title', 'description', 'thumbnail', 'content',]

class BlogEditForm(BlogAddForm):
    tags = forms.CharField(help_text='Additional Tags still need to be separated by commas', label="Add Additional Tags", required=False)
