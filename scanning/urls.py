from django.urls import path

from scanning import views

urlpatterns = [
    path('', views.ScanningView.as_view(), name='scanning'),
    path('generate/', views.scanning_generate_view)
]
