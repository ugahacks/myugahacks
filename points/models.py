from django.db import models

from user.models import User


# Create your models here.

class Points(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    points = models.IntegerField(default=0)

    # TODO: Add self.save()
    def add_points(self, value):
        self.points += value
