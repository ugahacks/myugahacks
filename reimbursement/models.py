# coding=utf-8
from __future__ import unicode_literals

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from reimbursement import emails
from user.models import User

DEFAULT_EXPIRY_DAYS = settings.REIMBURSEMENT_EXPIRY_DAYS


def check_friend_emails(friend_emails, user_email):
    emails = friend_emails.replace(' ', '').split(',')
    if user_email in emails:
        raise Exception('%s is your own email' % user_email)
    for email in emails:
        try:
            user = User.objects.get(email=email)
        except:
            raise Exception('%s is not a registered hacker' % email)

        try:
            if user.reimbursement.waitlisted():
                raise Exception('%s has a waitlisted reimbursement' % email)
            if user.reimbursement.expired:
                raise Exception('%s reimbursement is expired' % email)
            if user.reimbursement.is_draft():
                raise Exception('%s reimbursement is still under revision' % email)
            if user.reimbursement.status == Reimbursement.APPROVED:
                raise Exception('%s already has an accepted reimbursement' % email)
            if user.reimbursement.status == Reimbursement.FRIEND_SUBMISSION:
                raise Exception('%s already has an accepted reimbursement' % email)

        except Reimbursement.DoesNotExist:
            raise Exception('%s didn\'t ask for reimbursement' % email)


class Reimbursement(models.Model):
    DRAFT = 'D'
    WAITLISTED = 'W'
    PEND_TICKET = 'PT'
    PEND_APPROVAL = 'PA'
    APPROVED = 'A'
    EXPIRED = 'X'
    FRIEND_SUBMISSION = 'FS'

    STATUS = [
        (DRAFT, 'Pending review'),
        (WAITLISTED, 'Wait listed'),
        (PEND_TICKET, 'Pending receipt submission'),
        (PEND_APPROVAL, 'Pending receipt approval'),
        (APPROVED, 'Receipt approved'),
        (EXPIRED, 'Expired'),
        (FRIEND_SUBMISSION, 'Friend submission'),
    ]

    # Admin controlled
    assigned_money = models.FloatField(null=True, blank=True)
    reimbursement_money = models.FloatField(null=True, blank=True)
    public_comment = models.CharField(max_length=300, null=True, blank=True)

    # User controlled
    paypal_email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    venmo_user = models.CharField(max_length=40, null=True, blank=True)
    receipt = models.FileField(null=True, blank=True, upload_to='receipt', )
    multiple_hackers = models.BooleanField(default=False)
    friend_emails = models.CharField(null=True, blank=True, max_length=400)
    origin = models.CharField(max_length=300)

    # If a friend submitted receipt
    friend_submission = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='friend_submissions',
                                          null=True, blank=True)

    # Meta
    hacker = models.OneToOneField('user.User', primary_key=True, on_delete=models.CASCADE)
    reimbursed_by = models.ForeignKey(User, null=True, blank=True, related_name='reimbursements_made',
                                      on_delete=models.CASCADE)
    expiration_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(default=timezone.now)
    creation_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=2, choices=STATUS,
                              default=DRAFT)

    @property
    def max_assignable_money(self):
        if self.friend_submission:
            return 0
        if not self.multiple_hackers:
            return self.assigned_money
        return sum([reimb.assigned_money for reimb in self.friend_submissions.all()]) + self.assigned_money

    @property
    def friend_emails_list(self):
        if not self.multiple_hackers:
            return None
        return self.friend_emails.replace(' ', '').split(',')

    @property
    def timeleft_expiration(self):
        if not self.expiration_time:
            return None
        return self.expiration_time - timezone.now()

    @property
    def expired(self):
        return self.status == self.EXPIRED

    def generate_draft(self, application):
        if self.status != self.DRAFT:
            return
        self.origin = application.origin
        self.assigned_money = application.reimb_amount
        self.hacker = application.user
        self.save()

    def expire(self):
        self.status = self.EXPIRED
        self.save()

    def send(self, user):
        if not self.assigned_money:
            raise ValidationError('Reimbursement can\'t be sent because '
                                  'there\'s no assigned money')
        if self.status == self.DRAFT:
            self.status = self.PEND_TICKET
            self.status_update_date = timezone.now()
            self.reimbursed_by = user
            self.reimbursement_money = None
            self.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRY_DAYS)
            self.save()

    def no_reimb(self, user):
        if self.status == self.DRAFT:
            self.status = self.WAITLISTED
            self.status_update_date = timezone.now()
            self.reimbursed_by = user
            self.reimbursement_money = 0
            self.assigned_money = 0
            self.save()

    def is_sent(self):
        return self.status in [self.PEND_APPROVAL, self.PEND_TICKET, ]

    def has_friend_submitted(self):
        return self.status == self.FRIEND_SUBMISSION

    def is_draft(self):
        return self.status == self.DRAFT

    def is_accepted(self):
        return self.status in self.APPROVED

    def waitlisted(self):
        return self.status == self.WAITLISTED

    def needs_action(self):
        return self.can_submit_receipt()

    def can_submit_receipt(self):
        return self.status == self.PEND_TICKET and not self.expired and not self.hacker.application.is_rejected()

    def reject_receipt(self, user, request):
        self.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRY_DAYS)
        self.status = self.PEND_TICKET
        self.reimbursed_by = user
        self.reimbursement_money = None
        self.receipt.delete()
        if self.multiple_hackers:
            for reimb in self.friend_submissions.all():
                reimb.friend_submission = None
                reimb.reimbursement_money = None
                reimb.expiration_time = timezone.now() + timedelta(days=DEFAULT_EXPIRY_DAYS)
                reimb.public_comment = 'Your friend %s submission has not been accepted' % self.hacker.get_full_name()
                reimb.status = self.PEND_TICKET
                reimb.save()
        return emails.create_reject_receipt_email(self, request)

    def accept_receipt(self, user):
        self.status = self.APPROVED
        self.reimbursed_by = user
        self.reimbursement_money = min(self.reimbursement_money, self.max_assignable_money)

    def submit_receipt(self):
        self.status = self.PEND_APPROVAL
        self.public_comment = None
        self.friend_submission = None
        self.reimbursement_money = None
        if self.multiple_hackers:
            for reimb in Reimbursement.objects.filter(hacker__email__in=self.friend_emails_list):
                reimb.friend_submission = self
                reimb.status = self.FRIEND_SUBMISSION
                reimb.public_comment = None
                reimb.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_time = timezone.now()
        super(Reimbursement, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)
