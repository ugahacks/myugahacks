from django import forms
from .models import Blog
from froala_editor.widgets import FroalaEditor

class BlogAddForm(forms.ModelForm):
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256, help_text='Briefly describe the content of your blog post (This will appear when looking at the list of blog posts).')
    thumbnail = forms.ImageField()
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Blog
        fields = ['title', 'description', 'thumbnail', 'content', 'tags']
