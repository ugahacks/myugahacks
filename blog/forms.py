from django import forms
from .models import Blog
from froala_editor.widgets import FroalaEditor

class BlogAddForm(forms.ModelForm):
    title = forms.CharField(max_length=256)
    description = forms.CharField(max_length=256)
    tags = forms.CharField(help_text='Enter tags seperated by commas.')
    thumbnail = forms.ImageField()
    content = forms.CharField(widget=FroalaEditor)

    class Meta:
        model = Blog
        fields = ['title', 'description', 'thumbnail', 'content',]
