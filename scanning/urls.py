from django.urls import include, path
from scanning import views

urlpatterns = [
    path('', views.ScanningView.as_view(), name='scanning')
]
