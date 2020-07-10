from django.urls import path, re_path

from sponsors import views

app_name = 'sponsors'

urlpatterns = [
    re_path(r'^app_detail/(?P<id>[\w-]+)$', views.ApplicationDetailViewSponsor.as_view(), name='app_detail_sponsor'),
    path('', views.SponsorHomePage.as_view(), name='sponsor_home'),
    path('application/', views.SponsorApplicationView.as_view(), name='sponsor_application'),
    path('manage/add/', views.SponsorAdd.as_view(), name='sponsor_add'),
    path('manage/list', views.SponsorList.as_view(), name='sponsor_list'),
    path('manage/update/<int:pk>/', views.SponsorUpdate.as_view(), name='sponsor_update'),
    path('scanned_list/', views.SponsorScannedList.as_view(), name='sponsor_scanned_list'),
]
