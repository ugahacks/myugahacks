import typing as t

from django.conf import settings
from django.core import mail

from app import emails
from app.utils import reverse

from applications.models import Application

def create_invite_email(application, request):
    c = {
        'name': application.user.get_full_name,
        'reimb': getattr(application.user, 'reimbursement', None),
        'confirm_url': str(reverse('confirm_app', request=request, kwargs={'id': application.uuid_str})),
        'cancel_url': str(reverse('cancel_app', request=request, kwargs={'id': application.uuid_str})),
        'IS_ONLINE_HACKATHON': settings.IS_ONLINE_HACKATHON,
    }
    return emails.render_mail('mails/invitation',
                              application.user.email, c)


def create_waitlist_email(application, request):
    c = {
        'name': application.user.get_full_name
    }
    return emails.render_mail('mails/waitlist',
                              application.user.email, c)


def create_confirmation_email(application, request):
    c = {
        'name': application.user.get_full_name,
        'token': application.uuid_str,
        'qr_url': 'http://chart.googleapis.com/chart?cht=qr&chs=350x350&chl=%s'
                  % application.uuid_str,
        'cancel_url': str(reverse('cancel_app', request=request, kwargs={'id': application.uuid_str})),
        'IS_ONLINE_HACKATHON': settings.IS_ONLINE_HACKATHON,
    }
    return emails.render_mail('mails/confirmation',
                              application.user.email, c)


def create_lastreminder_email(application):
    c = {
        'name': application.user.get_full_name,
        # We need to make sure to redirect HTTP to HTTPS in production
        'confirm_url': 'http://%s%s' % (settings.HACKATHON_DOMAIN,
                                        reverse('confirm_app', kwargs={'id': application.uuid_str})),
        'cancel_url': 'http://%s%s' % (settings.HACKATHON_DOMAIN,
                                       reverse('cancel_app', kwargs={'id': application.uuid_str})),
    }
    return emails.render_mail('mails/last_reminder',
                              application.user.email, c, action_required=True)


def send_batch_emails(emails):
    connection = mail.get_connection()
    connection.send_messages(emails)


def create_online_checkin_email(application: Application) -> t.Any:
    context = {
        'name': application.user.get_full_name,
        'checkin_url': f'http://{settings.HACKATHON_DOMAIN}/checkin/me/{application.uuid}',
        'IS_ONLINE_HACKATHON': settings.IS_ONLINE_HACKATHON,
    }
    return emails.render_mail('mails/online_checkin', application.user.email, context, action_required=True)


def create_post_event_email(application: Application) -> t.Any:
    context = {
        'name': application.user.get_full_name,
        'recruit_url': 'https://ugeorgia.ca1.qualtrics.com/jfe/form/SV_5orFOdgzddQwY74',
        'cert_url': 'https://my.ugahacks.com/static/docs/proof_of_attendance.pdf',
        'photos_url': 'https://photos.google.com/share/AF1QipPftVrQsQ2hrI0biMNr5qdGpRBx1rn89GHhJR87u4NaelK61_m7DYCnnoc2QkOQOg?key=NDRWeGk4cFRnNzJWdGxvOWJNeGlGY1NEVnd4eVVB'
    }
    return emails.render_mail('mails/post_event', application.user.email, context)
