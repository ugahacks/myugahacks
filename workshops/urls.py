from django.conf.urls import url
from workshops import views

urlpatterns = [
    url(r'^add/$', views.WorkshopAdd.as_view(), name='workshop_add'),
    url(r'^list/$', views.WorkshopList.as_view(), name='workshop_list'),
]
