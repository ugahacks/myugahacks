from django.db import models
from user.models import User
from taggit.managers import TaggableManager

class Blog(models.Model):

    title = models.CharField(max_length=256, unique=True)

    description = models.CharField(max_length=256)

    thumbnail = models.ImageField(upload_to='blog/blog_thumbnails')

    publication_date = models.DateTimeField()

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.CharField(max_length=16384)

    tags = TaggableManager()
    
    approved = models.BooleanField(default=False)

    def tags_as_str(self):
        return ', '.join([str(t) for t in list(self.tags.all())])

    def __lt__(self, other):
        return self.publication_date > other.publication_date

    def format_publication_date(self):
        return self.publication_date.strftime("%m {0} %d {0} %y").format("\u2022")
