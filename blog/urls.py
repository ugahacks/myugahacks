from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogHome.as_view(), name='blog_home'),
    path('add/', views.BlogAdd.as_view(), name='blog_add'),
    path('full/<int:pk>/', views.BlogDetail.as_view(), name='blog_detail'),
    path('edit/<int:pk>/', views.BlogEdit.as_view(), name='blog_edit'),
]