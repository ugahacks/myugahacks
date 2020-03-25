from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Points

# Create your views here.

class PointsHomeView(TemplateView):

    template_name = 'points_home.html'

    #TODO: Deny access if user is not authenticated.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Points.objects.get(user=self.request.user)
        points = user.points
        context = {
            'points': points,
        }
        return context
