from django.urls import path

from archives import views

urlpatterns = [
    path('', views.UGAHacks5View.as_view(), name='UGAHacks5'),
]
