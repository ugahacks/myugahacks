from django.conf.urls import url
from workshops import views


urlpatterns = [
    url(r'^list/$', views.WorkshopsList.as_view(), name='workshops_list'),
    url(r'^add/$', views.WorkshopAdd.as_view(), name='workshop_add'),
    url(r'^users/$', views.WorkshopsUsers.as_view(), name='workshops_users'),
    url(r'^(?P<id>[\w-]+)$', views.WorkshopDetail.as_view(), name='workshop_detail'),
    url(r'^scan/(?P<id>[\w-]+)$', views.WorkshopsCheckin.as_view(), name='workshop_checkin'),
    url(r'^api/$', views.WorkshopsApi.as_view(), name='workshops_api'),
    url(r'^api/checkin$', views.WorkshopsCoolAPI.as_view(), name='cool_workshops_api')
]
