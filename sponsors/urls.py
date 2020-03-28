from django.urls import include, path, re_path
from sponsors import views

urlpatterns = [
    path('application/', views.SponsorApplication.as_view(), name='sponsor_application'),
    path('manage/add/', views.AddSponsor.as_view(), name='add_sponsor'),
    path('', views.SponsorHomePage.as_view(), name='sponsor_home'),
    re_path(r'^(?P<id>[\w-]+)$', views.ApplicationDetailViewSponsor.as_view(), name = 'app_detail_sponsor'),
]
