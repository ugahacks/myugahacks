from django.urls import path

from . import views

urlpatterns = [
    path('', views.PointsHomeView.as_view(), name='points-home'),
]
