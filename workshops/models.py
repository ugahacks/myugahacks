from django.db import models
from user.models import User

class Workshop(models.Model):
	title = models.CharField(max_length=63, null=False)

	description = models.CharField(max_length=300, null=True)

	#Should be specified by an admin after it is added.
	location = models.CharField(max_length=63, null=True, blank=True)

	host = models.CharField(max_length=63, null=False)

	open = models.BooleanField(null=False, default=False)

	#I got really upset because i couldnt reverse reference Timeslots since it
	#has two workshop foreign keys, so im including these fields as well. >:(
	#It is really redundant but im tilted.
	start = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

	end = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

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


	#models.SET_NULL is used so when a workshop is deleted, the timeslot is not deleted along with it.
	workshop_one = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='workshop_one_set')

	workshop_two = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='workshop_two_set')

    #Intended use is the list the timeslot for users.
	def __str__(self):
		return f'{str(self.start.strftime("%D %I:%M %p"))} to {str(self.end.strftime("%D %I:%M %p"))}'

class Attendance(models.Model):
	workshop = models.ForeignKey(Workshop, null=False, on_delete=models.CASCADE)

	user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
