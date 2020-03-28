from django.conf.urls import url
from scanning import views

urlpatterns = [
    url(r'^scan/$', views.Scanner.as_view(), name='scanner'),
]
