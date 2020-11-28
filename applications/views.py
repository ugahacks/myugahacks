# Create your views here.
from __future__ import print_function

import logging
from datetime import timedelta

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from app import slack
from app.slack import SlackInvitationException
from app.utils import reverse, hacker_tabs
from app.views import TabsView
from applications import emails, forms
from applications.models import Application, DraftApplication
from user.mixins import IsHackerMixin, is_hacker


def check_application_exists(user, uuid):
    try:
        application = Application.objects.get(user=user)
    except Application.DoesNotExist:
        raise Http404
    if not application or uuid != application.uuid_str:
        raise Http404


class ConfirmApplication(IsHackerMixin, UserPassesTestMixin, View):
    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get(self, request, *args, **kwargs):
        application = Application.objects.get(user=request.user)
        msg = None
        if application.can_confirm():
            msg = emails.create_confirmation_email(application, self.request)
        try:
            application.confirm()
        except:
            raise Http404

        if msg:
            msg.send()
            try:
                slack.send_slack_invite(request.user.email)
            # Ignore if we can't send, it's only optional
            except SlackInvitationException as e:
                logging.error(e)

        return http.HttpResponseRedirect(reverse('dashboard'))


class CancelApplication(IsHackerMixin, UserPassesTestMixin, TabsView):
    template_name = 'cancel.html'

    def test_func(self):
        check_application_exists(self.request.user, self.kwargs.get('id', None))
        return True

    def get_back_url(self):
        return reverse('dashboard')

    def get_context_data(self, **kwargs):
        context = super(CancelApplication, self).get_context_data(**kwargs)

        application = Application.objects.get(user=self.request.user)
        context.update({'application': application, })
        if application.status == Application.CANCELLED:
            context.update({'error': "Thank you for responding. We're sorry you won't be able to make it."
                                     " Hope to see you next edition!"
                            })
        elif application.status == Application.EXPIRED:
            context.update({'error': "Unfortunately your invite has expired."})
        elif not application.can_be_cancelled():
            context.update({
                'error': "You found a glitch! You can't cancel this invitation. Is this the question for 42?",
                'application': None
            })
        return context

    def post(self, request, *args, **kwargs):
        application = Application.objects.get(user=self.request.user)
        try:
            application.cancel()
        except ValidationError:
            pass

        return http.HttpResponseRedirect(reverse('dashboard'))


def get_deadline(application):
    last_updated = application.status_update_date
    if application.status == Application.INVITED:
        deadline = last_updated + timedelta(days=5)
    else:
        deadline = last_updated + timedelta(days=1)
    return deadline


class HackerDashboard(IsHackerMixin, TabsView):
    template_name = 'dashboard.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerDashboard, self).get_context_data(**kwargs)
        try:
            draft = DraftApplication.objects.get(user=self.request.user)
            form = forms.ApplicationForm(instance=Application(**draft.get_dict()))
        except:
            form = forms.ApplicationForm()
        context.update({'form': form})
        try:
            application = Application.objects.get(user=self.request.user)
            deadline = get_deadline(application)
            context.update({'invite_timeleft': deadline - timezone.now()})
        except:
            # We ignore this as we are okay if the user has not created an application yet
            pass

        return context

    def post(self, request, *args, **kwargs):
        new_application = True
        try:
            form = forms.ApplicationForm(request.POST, request.FILES, instance=request.user.application)
            new_application = False
        except:
            form = forms.ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            if new_application:
                messages.success(request,
                                 'We have now received your application. '
                                 'Processing your application will take some time, so please be patient.')
            else:
                messages.success(request, 'Application changes saved successfully!')

            return HttpResponseRedirect(reverse('root'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


class HackerApplication(IsHackerMixin, TabsView):
    template_name = 'application.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(HackerApplication, self).get_context_data(**kwargs)
        application = get_object_or_404(Application, user=self.request.user)
        deadline = get_deadline(application)
        context.update(
            {'invite_timeleft': deadline - timezone.now(), 'form': forms.ApplicationForm(instance=application)})
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = forms.ApplicationForm(request.POST, request.FILES, instance=request.user.application)
        except:
            form = forms.ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()

            messages.success(request, 'Application changes saved successfully!')

            return HttpResponseRedirect(reverse('dashboard'))
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)


@is_hacker
def save_draft(request):
    d = DraftApplication()
    d.user = request.user
    form_keys = set(dict(forms.ApplicationForm().fields).keys())
    valid_keys = set([field.name for field in Application()._meta.get_fields()])
    d.save_dict(dict((k, v) for k, v in request.POST.items() if k in valid_keys.intersection(form_keys) and v))
    d.save()
    return JsonResponse({'saved': True})


def export_resume(request):
    try:
        response = HttpResponse(open("./files/resumes/resume_export.tar.gz", 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=resume_export.tar.gz'
        return response
    except:
        raise Http404

def export_newsletter_subs(request):
    try:
        response = HttpResponse(open("./files/newsletter_subs.csv", 'rb').read())
        response['Content-Type'] = 'text/plain'
        response['Content-Disposition'] = 'attachment; filename=newsletter_subs.csv'
        return response
    except:
        raise Http404
