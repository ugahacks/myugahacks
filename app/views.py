import os
from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
# from baggage.models import Bag
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from app import mixins
from applications.models import Application
from blog.models import Blog
from reimbursement.models import Reimbursement


def root_view(request):
    if not request.user.is_authenticated:
        return render(request, 'ugahacks6/mainpage.html')
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('account_login'))
    if not request.user.has_usable_password():
        return HttpResponseRedirect(reverse('set_password'))
    if not request.user.email_verified:
        return HttpResponseRedirect(reverse('verify_email_required'))
    if request.user.is_organizer:
        return HttpResponseRedirect(reverse('review'))
    elif request.user.is_volunteer:
        return HttpResponseRedirect(reverse('check_in_list'))
    elif request.user.is_sponsor:
        return HttpResponseRedirect(reverse('sponsors:sponsor_application'))
    return HttpResponseRedirect(reverse('dashboard'))


def code_conduct(request):
    code_link = getattr(settings, 'CODE_CONDUCT_LINK', None)
    if code_link:
        return HttpResponseRedirect(code_link)
    return render(request, 'code_conduct.html')


def legal_notice(request):
    return render(request, 'legal_notice.html')


def privacy_and_cookies(request):
    return render(request, 'privacy_and_cookies.html')


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')


def protectedMedia(request, file_):
    path, file_name = os.path.split(file_)
    downloadable_path = None
    if path == "resumes":
        app = get_object_or_404(Application, resume=file_)
        if request.user.is_authenticated and (request.user.is_organizer or
                                              (app and (app.user_id == request.user.id))):
            downloadable_path = app.resume.path
    elif path == "blog_thumbnails":
        blog = get_object_or_404(Blog, thumbnail=file_)
        downloadable_path = blog.thumbnail.path
    elif path == "receipt":
        app = get_object_or_404(Reimbursement, receipt=file_)
        if request.user.is_authenticated and (request.user.is_organizer or
                                              (app and (app.hacker_id == request.user.id))):
            downloadable_path = app.receipt.path
    elif path == "baggage":
        bag = get_object_or_404(Bag, image=file_)
        if request.user.is_authenticated and (request.user.is_organizer or request.user.is_volunteer):
            downloadable_path = bag.image.path
    if downloadable_path:
        response = StreamingHttpResponse(open(downloadable_path, 'rb'))
        response['Content-Type'] = ''
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % quote(file_name)
        response['Content-Transfer-Encoding'] = 'binary'
        response['Expires'] = '0'
        response['Cache-Control'] = 'must-revalidate'
        response['Pragma'] = 'public'
        return response
    return HttpResponseRedirect(reverse('account_login'))


class TabsView(mixins.TabsViewMixin, TemplateView):
    pass


class SponsorshipPacketView(TemplateView):
    template_name = 'sponsorship_deck.html'
