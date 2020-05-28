from django.urls import include, path, re_path
from sponsors import views

app_name = 'sponsors'

urlpatterns = [
    path('application/', views.SponsorApplicationView.as_view(), name='sponsor_application'),
    path('manage/add/', views.SponsorAdd.as_view(), name='sponsor_add'),
    path('manage/list', views.SponsorList.as_view(), name='sponsor_list'),
    path('', views.SponsorHomePage.as_view(), name='sponsor_home'),
    path('manage/update/<int:pk>/', views.SponsorUpdate.as_view(), name='sponsor_update'),
    re_path(r'^(?P<id>[\w-]+)$', views.ApplicationDetailViewSponsor.as_view(), name = 'app_detail_sponsor'),
]
