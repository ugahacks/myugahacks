from datetime import timedelta

from django.db import models

from user.models import User


class Workshop(models.Model):
    title = models.CharField(max_length=63, null=False)

    description = models.CharField(max_length=300, null=True)

    # Should be specified by an admin after it is added.
    location = models.CharField(max_length=63, null=True, blank=True)

    host = models.CharField(max_length=63, null=False)

    open = models.BooleanField(null=False, default=False)

    # Amount of points awarded if user attends this workshop
    points = models.IntegerField(default=0)

    def __str__(self):
        return str(self.title)

    def time_period(self):
        # Time printed is 5 hours ahead so i just adjust it manually.
        adjusted_start = self.get_time_slot().start - timedelta(hours=5)
        adjusted_end = self.get_time_slot().end - timedelta(hours=5)
        return f'{adjusted_start.strftime("%m/%d %l:%M %p")} to {adjusted_end.strftime("%m/%d %l:%M %p")}'

    # Finds the timeslot associated with this workshop. Needed for tables.py !
    def get_time_slot(self):
        timeslot = Timeslot.objects.filter(workshop_one=self).first()
        if not timeslot:
            timeslot = Timeslot.objects.filter(workshop_two=self).first()
        return timeslot


# Attended model not implemented yet. Ignore this for now.
# def attended(self):
# return Attended.objects.filter(workshop=self).count()


class Timeslot(models.Model):
    start = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

    end = models.DateTimeField(auto_now=False, auto_now_add=False, null=False)

    # models.SET_NULL is used so when a workshop is deleted, the timeslot is not deleted along with it.
    workshop_one = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                     related_name='workshop_one_set')

    workshop_two = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True, default=None,
                                     related_name='workshop_two_set')

    # Intended use is the list the timeslot for users.
    def __str__(self):
        # Time printed is 5 hours ahead so i just adjust it manually.
        adjusted_start = self.start - timedelta(hours=5)
        adjusted_end = self.end - timedelta(hours=5)
        return f'{adjusted_start.strftime("%m/%d %l:%M %p")} to {adjusted_end.strftime("%m/%d %l:%M %p")}'


class Attendance(models.Model):
    workshop = models.ForeignKey(Workshop, null=False, on_delete=models.CASCADE)

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
