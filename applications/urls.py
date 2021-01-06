from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from applications import views

urlpatterns = [
    url(r'^applications/(?P<id>[\w-]+)/confirm$', login_required(views.ConfirmApplication.as_view()),
        name='confirm_app'),
    url(r'^applications/(?P<id>[\w-]+)/cancel$', login_required(views.CancelApplication.as_view()),
        name='cancel_app'),
    url(r'^dashboard/$', views.HackerDashboard.as_view(), name='dashboard'),
    url(r'^applications/$', views.HackerApplication.as_view(), name='application'),
    url(r'^application/draft/$', views.save_draft, name='save_draft'),
    url(r'^export/resume$', views.export_resume, name='export_resume'),
    url(r'^export/newsletter$', views.export_newsletter_subs, name='export_newsletter'),
    url(r'^export/inperson$', views.export_in_person_apps, name='export_in_person_apps')
]
