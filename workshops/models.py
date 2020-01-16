from django.db import models
from user.models import User
from django.template import defaultfilters
from datetime import timedelta


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

	def time_period(self):
		#Time printed is 5 hours ahead so i just adjust it manually.
		adjusted_start = self.start - timedelta(hours=5)
		adjusted_end = self.end - timedelta(hours=5)
		return f'{adjusted_start.strftime("%m/%d %X")} to {adjusted_end.strftime("%m/%d %X")}'


	#Attended model not implemented yet. Ignore this for now.
	#def attended(self):
		#return Attended.objects.filter(workshop=self).count()

#Todo:
class Timeslot(models.Model):
	start = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

	end = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)


	#models.SET_NULL is used so when a workshop is deleted, the timeslot is not deleted along with it.
	workshop_one = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='workshop_one_set')

	workshop_two = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name='workshop_two_set')

    #Intended use is the list the timeslot for users.
	def __str__(self):
		#Time printed is 5 hours ahead so i just adjust it manually.
		adjusted_start = self.start - timedelta(hours=5)
		adjusted_end = self.end - timedelta(hours=5)
		return f'{adjusted_start.strftime("%d/%m %X")} to {adjusted_end.strftime("%d/%m %X")}'

class Attendance(models.Model):
	workshop = models.ForeignKey(Workshop, null=False, on_delete=models.CASCADE)

	user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
