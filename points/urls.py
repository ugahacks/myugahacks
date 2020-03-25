from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.PointsHomeView.as_view(), name='points-home'),
]
