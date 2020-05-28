from django.views import View
from django.views.generic.base import TemplateView

from .models import Points


# Create your views here.

class PointsHomeView(TemplateView):
    template_name = 'points_home.html'

    # TODO: Deny access if user is not authenticated.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Points.objects.get(user=self.request.user)
        points = user.points
        context = {
            'points': points,
        }
        return context


class AddPointsView(View):
    # Pass data from JS to here. (qr(user) and amount of points to be added.)
    def post(self, request, *args, **kwargs):
        qr_id = request.POST.get('qr_code', None)
        points = request.POST.get('points', None)

        # TODO: Add error handling for below
        # Checkin object of a participants
        hacker_checkin = CheckIn.objects.filter(qr_identifier=qr_id).first()

        # The user model
        hacker = hacker_checkin.application.user

        # Points model with user
        hacker_points = Points.objects.filter(user=hacker)

        if hacker_points:
            hacker_points[0].points += points
            hacker_points[0].save()
        else:
            pass
            # Error handling.
