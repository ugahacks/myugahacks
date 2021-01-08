from django.conf.urls import url
from django.urls import path

from workshops import views

urlpatterns = [
    url(r'^add/$', views.WorkshopAdd.as_view(), name='workshop_add'),
    url(r'^list/$', views.WorkshopList.as_view(), name='workshop_list'),
    url(r'^detail/(?P<pk>\d+)/$', views.WorkshopDetail.as_view(), name='workshop_detail'),
    url(r'^scan/(?P<id>[\w-]+)$', views.WorkshopCheckin.as_view(), name='workshop_checkin'),
    url(r'^update/(?P<pk>\d+)/$', views.WorkshopUpdate.as_view(), name='workshop_update'),
    path('attendance/<int:workshop_id>/', views.workshop_attend, name='workshop_attend'),
]
