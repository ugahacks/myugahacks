from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blogadmin'

urlpatterns = [
    path('', views.BlogAdminHome.as_view(), name='blog_admin_home'),
    path('full/<int:pk>/', views.BlogAdminDetail.as_view(), name='blog_admin_detail'),
    path('approve/<int:blog_id>/', views.BlogAdminApprove.as_view(), name='blog_admin_approve')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
