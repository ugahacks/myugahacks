from django.core import mail
from django.core.management.base import BaseCommand

from applications import emails
from app.emails import render_mail
from applications.models import Application


class Command(BaseCommand):
    help = f'Command utility for sending out online check-in emails. \
            To send emails to all confirmed applicants, run the command with \
            the --all option. Non-Functional Test Example: \
            send_online_checkin_emails --test <addr> <addr> --no-func.'

    def add_arguments(self, parser):
        # positional arguments here:

        # named (optional) arguments here:
        parser.add_argument(
            '--test',
            nargs='+',
            type=str,
            metavar='EMAIL_ADDR',
            help='allows for testing of N-specified emails; \
                    specify --no-func to send directly, otherwise emails \
                    will pass-through UGAHacks <Application> system.',
        )

        parser.add_argument(
            '--no-func',
            action='store_true',
            help='send only non-functional emails (no working /checkin/me/<uuid> links).',
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='to avoid accidental emails, a purposeful --all argument must be \
                    included to send out checkin emails to all CONFIRMED applications.'
        )

    def handle(self, *args, **options):

        # self.stdout.write(f'args: {args}\noptions: {options}')

        if options['test'] is not None:
            if options['no_func']:
                self.stdout.write(f'Sending out {len(options["test"])} non-functional emails...')
                
                messages = []
                
                for email_addr in options['test']:
                    messages.append(render_mail('mails/online_checkin', 
                        email_addr, {'name': 'NON_FUNC_TEST', 'IS_ONLINE_HACKATHON': True}, 
                        action_required=True))

                mail.get_connection().send_messages(messages)
                success_message = f'Successfully sent {len(messages)} ' \
                                    + 'non-functional checkin emails.'

                self.stdout.write(self.style.SUCCESS(success_message))
            else:
                attempt_message = f'Attempting to send out {len(options["test"])} ' \
                                    + 'functional emails...'
                reminder_message = f'Remember: functional emails can only be sent to ' \
                                    + 'applications with CONFIRMED status.'

                self.stdout.write(attempt_message)
                confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
                self.stdout.write(reminder_message)

                messages = []
                for email_addr in options['test']:
                    application = confirmed_applications.get(user__email=email_addr)
                    messages.append(emails.create_online_checkin_email(application))
                mail.get_connection().send_messages(messages)
                success_message = f'Successfully sent {len(messages)} functional checkin emails.'
                self.stdout.write(self.style.SUCCESS(success_message))

        elif options['all']:
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
        else:
            self.stdout.write(self.style.ERROR(f'Must specify: --all or --test. See --help.'))
