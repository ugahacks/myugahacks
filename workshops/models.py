from django.db import models
from user.models import User

# Create your models here.
class Workshop(models.Model):
	title = models.CharField(max_length=63, null=False)

	location = models.CharField(max_length=63, null=False)

	host = models.CharField(max_length=63, null=False)

	starts = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)

	ends = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)

	opened = models.BooleanField(null=False, default=False)

	def __str__(self):
		return str(self.name)

	def attended(self):
		return Attended.objects.filter(workshop=self).count()

class Attended(models.Model):
	workshop = models.ForeignKey(Workshop, null=False, on_delete=models.CASCADE)

	user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

	time = models.DateTimeField(auto_now=False, auto_now_add=True)