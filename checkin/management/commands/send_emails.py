from django.core import mail
from django.core.management.base import BaseCommand

from applications import emails
from app.emails import render_mail
from applications.models import Application

import time

class Command(BaseCommand):
    help = f'Command utility for sending out online check-in emails. \
            To send emails to all confirmed applicants, run the command with \
            the --all option. Non-Functional Test Example: \
            [send_emails --template online_checkin --to <addr> <addr> --func] or \
            [send_emails --template online_checkin --all].'

    def add_arguments(self, parser):
        # positional arguments here:

        # named (optional) arguments here:
        parser.add_argument(
            '--template',
            type=str,
            metavar='TEMPLATE',
            help='specify the <template> to test. \
                    these can be found in applications/emails.py',
        )

        parser.add_argument(
            '--to',
            nargs='+',
            type=str,
            metavar='EMAIL_ADDR',
            help='[recipient] allows for testing of N-specified emails; \
                    specify --no-func to send directly, otherwise emails \
                    will pass-through UGAHacks <Application> system.',
        )

        parser.add_argument(
            '--func',
            action='store_true',
            help='send functional emails (e.g. working /checkin/me/<uuid> links). \
            these will pass through the UGAHacks ecosystem.',
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='[recipient] to avoid accidental emails, a purposeful --all argument must be \
                    included to send out checkin emails to all CONFIRMED applications. note: \
                    sending any template expect <online_checkin> via --all will fail.'
        )

    def handle(self, *args, **options):

        if options['template']:

            if options['to'] is not None:
                if options['func']:
                    if options['template'] == 'online_checkin':
                        attempt_message = f'Attempting to send out {len(options["to"])} ' \
                                        + 'functional emails...'
                        reminder_message = f'Remember: functional emails can only be sent to ' \
                                            + 'applications with CONFIRMED status.'

                        self.stdout.write(attempt_message)
                        confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
                        self.stdout.write(reminder_message)

                        messages = []
                        for email_addr in options['to']:
                            application = confirmed_applications.get(user__email=email_addr)
                            messages.append(emails.create_online_checkin_email(application))
                        mail.get_connection().send_messages(messages)
                        success_message = f'Successfully sent {len(messages)} functional checkin emails.'
                        self.stdout.write(self.style.SUCCESS(success_message))
                    else: # if you attempt to send a functional email that isn't a check-in email
                        self.stdout.write(self.style.ERROR(f'Cannot send functional {options["template"]}.'))
                else: # no functional emails
                    if options['template'] == 'online_checkin':
                        self.stdout.write(f'Sending out {len(options["to"])} non-functional emails...')
                    
                        messages = []
                        
                        for email_addr in options['to']:
                            messages.append(render_mail(f'mails/{options["template"]}', email_addr, 
                                {'name': 'NON_FUNC_TEST'},
                                action_required=True))

                        mail.get_connection().send_messages(messages)
                        success_message = f'Successfully sent {len(messages)} ' \
                                            + 'non-functional checkin emails.'

                        self.stdout.write(self.style.SUCCESS(success_message))
                    elif options['template'] == 'post_event':
                        self.stdout.write(f'Sending out {len(options["to"])} post_event (nonfunc) emails...')

                        messages = []

                        for email_addr in options['to']:
                            messages.append(render_mail(f'mails/{options["template"]}', email_addr, 
                                {'name': 'NON_FUNC_TEST'},
                                action_required=True))

                        mail.get_connection().send_messages(messages)
                        success_message = f'Successfully sent {len(messages)} ' \
                                            + 'non-functional checkin emails.'

                        self.stdout.write(self.style.SUCCESS(success_message))

            elif options['all']:
                if options['template'] == 'online_checkin':
                    confirm_msg = f'Are you sure you want to send check-in emails ' \
                            + 'to ALL confirmed applications? [y/N] '
                    confirmed = input(confirm_msg)

                    if confirmed.lower() == 'y':

                        def chunk(mlist, n):
                            """Yield successive n-sized chunks from lst."""
                            for i in range(0, len(mlist), n):
                                yield mlist[i:i + n]

                        self.stdout.write('Gathering confirmed applications...')
                        confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
                        self.stdout.write(f'Found: {confirmed_applications.count()} confirmed applications.')
                        self.stdout.write('Sending self check-in emails...')

                        # gmail has a throttle @ 100 for emails; also doesn't like being spammed.
                        count = 0
                        conf_apps_count = confirmed_applications.count()
                        N_CHUNK_NO_THROTTLE = 50
                        THROTTLE_TIMEOUT = 120
                        if conf_apps_count >= N_CHUNK_NO_THROTTLE:
                            self.stdout.write(f'Due to gmail throttling, emails will be sent in batches.')

                        messages = []
                        for application in confirmed_applications:
                            messages.append(emails.create_online_checkin_email(application))
                        
                        chunked_messages = list(chunk(messages, N_CHUNK_NO_THROTTLE))

                        see_chunked = input('Would you like to see the generated chunks? [y/N] ')
                        if see_chunked.lower() == 'y':
                            for chunk in chunked_messages:
                                self.stdout.write(f'{"-" * 12}CHUNK{"-" * 12}')
                                self.stdout.write('\n'.join(map(lambda m: f'<{m.to}>', chunk)))
                                self.stdout.write(f'{"-" * 12}CHUNK{"-" * 12}')

                        proceed_with_emails = input('Would you like to proceed? [y/N] ')
                        if proceed_with_emails.lower() == 'y':
                            for chunk in chunked_messages:
                                self.stdout.write(f'Sending chunk{count + 1}...')
                                count += 1
                                connection = mail.get_connection()
                                connection.send_messages(chunk)
                                self.stdout.write(f'Sleeping for {THROTTLE_TIMEOUT}s...')
                                time.sleep(THROTTLE_TIMEOUT) # don't hurt gmail :(

                            self.stdout.write(self.style.SUCCESS(f'Successfully sent {len(messages)} check-in emails.'))
                    else:
                        self.stdout.write(f'Sent 0 check-in emails.')
                else:
                    self.stdout.write(self.style.ERROR(f'Cannot send <{options["template"]}> to all.'))
            
            else:
                self.stdout.write(self.style.ERROR(f'Must specify recipients. See --help.'))
        else:
            self.stdout.write(self.style.ERROR(f'Must specify a template. See --help.'))