from django.conf.urls import url

from checkin import views

from django.urls import path

urlpatterns = [
    url(r'^all/$', views.CheckInList.as_view(), name='check_in_list'),
    url(r'^ranking/$', views.CheckinRankingView.as_view(), name='check_in_ranking'),
    url(r'^reissue/$', views.ReIssueList.as_view(), name='re_issue_list'),
    url(r'^reissue/(?P<id>[\w-]+)$', views.ReIssueHackerView.as_view(), name='re_issue_hacker'),
    # url(r'(?P<id>[\w-]+)$', views.CheckInHackerView.as_view(), name='check_in_hacker'),

    # added to keep legacy use of regex pre-refactor
    # url(r'me/(?P<id>[\w-]+)$', views.OnlineCheckInHackerView.as_view(), name='online_check_in'),
    path('me/<uuid:id>', views.OnlineCheckInHackerView.as_view(), name='check_in_hacker'),
]
