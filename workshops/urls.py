from django.conf.urls import url
from workshops import views

urlpatterns = [
    url(r'^add/$', views.WorkshopAdd.as_view(), name='workshop_add'),
    url(r'^list/$', views.WorkshopList.as_view(), name='workshop_list'),
    url(r'^detail/(?P<pk>\d+)/$', views.WorkshopDetail.as_view(), name='workshop_detail'),
    url(r'^scan/(?P<id>[\w-]+)$', views.WorkshopCheckin.as_view(), name='workshop_checkin'),
]
