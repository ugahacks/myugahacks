from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogHome.as_view(), name='blog_home'),
    path('list/', views.BlogPostList.as_view(), name='blog_list'),
    path('add/', views.BlogAdd.as_view(), name='blog_add'),
]
