from django.db import models
from user.models import User

class Workshop(models.Model):
	title = models.CharField(max_length=63, null=False)

	description = models.CharField(max_length=300, null=True)

	location = models.CharField(max_length=63, null=False)

	host = models.CharField(max_length=63, null=False)

	open = models.BooleanField(null=False, default=False)

	def __str__(self):
		return str(self.title)

	#Attended model not implemented yet. Ignore this for now.
	#def attended(self):
		#return Attended.objects.filter(workshop=self).count()

#Todo:
#Time in the admin panel is not the time displayed to users for somereason. Needs to be fixed.
class Timeslot(models.Model):
	start = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

	end = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

	workshop_one = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='workshop_one_set')

	workshop_two = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='workshop_two_set')

    #Intended use is the list the timeslot for users.
	def __str__(self):
		return f'{str(self.start.strftime("%D %I:%M %p"))} to {str(self.end.strftime("%D %I:%M %p"))}'

'''
class Attended(models.Model):
	workshop = models.ForeignKey(Workshop, null=False, on_delete=models.CASCADE)

	user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
'''
