from django.urls import include, path
from sponsors import views

urlpatterns = [
    path('application/', views.SponsorApplication.as_view(), name='sponsor_application'),
    path('manage/add/', views.AddSponsor.as_view(), name='add_sponsor'),
    path('', views.sponsor_home, name='sponsor_home'),
]
