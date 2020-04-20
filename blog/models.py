from django.db import models
from froala_editor.fields import FroalaField
from user.models import User

class Blog(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=256)
    thumbnail = models.ImageField(upload_to='blog_thumbnails')
    publication_date = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = FroalaField()

class Tag(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    tag = models.CharField(max_length=32)

    def __str__(self):
        return self.tag
