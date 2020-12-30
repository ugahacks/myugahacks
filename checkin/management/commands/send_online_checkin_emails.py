from django.core import mail
from django.core.management.base import BaseCommand

from applications import emails
from applications.models import Application


class Command(BaseCommand):
    help = 'Command utility for sending out online check-in emails.'

    def handle(self, *args, **options):

        self.stdout.write('Gathering confirmed applications...')
        confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
        self.stdout.write(f'Found: {confirmed_applications.count()} confirmed applications.')
        self.stdout.write('Sending self check-in emails...')
        
        messages = []
        for application in confirmed_applications:
            messages.append(emails.create_online_checkin_email(application))
        connection = mail.get_connection()
        connection.send_messages(messages)

        self.stdout.write(self.style.SUCCESS(f'Successfully sent {len(messages)} check-in emails.'))
