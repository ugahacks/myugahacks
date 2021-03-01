from django.core import mail
from django.core.management.base import BaseCommand

from applications import emails
from app.emails import render_mail
from applications.models import Application

import time

class Command(BaseCommand):

    # prevents gmail from getting angry :)
    N_CHUNK_NO_THROTTLE = 50
    THROTTLE_TIMEOUT = 120


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
        # VALIDATE
        if not options['template']:
            self.stdout.write(self.style.ERROR(f'Must specify a template. See --help.'))
            return
        if not options['to'] and not options['all']:
            self.stdout.write(self.style.ERROR(f'Must specify recipients. See --help.'))
            return
        
        # RUN
        recipients = options['to'] or []
        template_name = options['template']
        num_recipients = len(recipients) or 'ALL'

        if options['all']: # non-test, functional emails
            if options['template'] == 'online_checkin':
                self.send_online_checkin_emails_to_all()
            elif options['template'] == 'post_event':
                self.send_post_event_emails_to_all()
            else:
                self.stdout.write(self.style.ERROR(f'Cannot send <{options["template"]}> to all.'))
        elif options['func']: # test, functional emails
            attempt_message = f'Attempting to send out {num_recipients} ' \
                                + f'functional {template_name} emails...'
            self.stdout.write(attempt_message)
            
            if template_name == 'online_checkin':
                self.send_test_online_checkin_emails(recipients, template_name)
            elif template_name == 'post_event':
                self.stdout.write(f'Functionality for --func<{template_name}> testing is not complete.')
                # self.send_test_post_event_emails(recipients, template_name)
            else:
                self.stdout.write(self.style.ERROR(f'Cannot send functional {options["template"]}.'))
        else: # test, non-functional emails
            self.send_template_test(template_name, recipients)


    
    def send_test_post_event_emails(self, recipients, template_name):
        messages = []
        reminder_message = f'Remember: functional emails can only be sent to ' \
                            + f'applications with ATTENDED status.'
        self.stdout.write(reminder_message)
        confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
                        
        for email_addr in recipients:
            application = confirmed_applications.get(user__email=email_addr)
            messages.append(emails.create_online_checkin_email(application))

        mail.get_connection().send_messages(messages)
        success_message = f'Successfully sent {len(messages)} functional {template_name} emails.'
        self.stdout.write(self.style.SUCCESS(success_message))




    def send_post_event_emails_to_all(self):
        confirm_msg = f'Are you sure you want to send post_event emails ' \
                            + 'to ALL confirmed applications? [y/N] '
        confirmed = input(confirm_msg)

        if confirmed.lower() == 'y':

            def chunk(mlist, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(mlist), n):
                    yield mlist[i:i + n]

            self.stdout.write('Gathering confirmed applications...')
            attended_applications = Application.objects.filter(status=Application.ATTENDED)
            self.stdout.write(f'Found: {attended_applications.count()} ATTENDED applications.')
            self.stdout.write('Sending self post_event emails...')

            # gmail has a throttle @ 100 for emails; also doesn't like being spammed.
            count = 0
            conf_apps_count = attended_applications.count()
            
            if conf_apps_count >= self.N_CHUNK_NO_THROTTLE:
                self.stdout.write(f'Due to gmail throttling, emails will be sent in batches.')

            messages = []
            for application in attended_applications:
                messages.append(emails.create_post_event_email(application))
            
            chunked_messages = list(chunk(messages, self.N_CHUNK_NO_THROTTLE))

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
                    self.stdout.write(f'Sleeping for {self.THROTTLE_TIMEOUT}s...')
                    time.sleep(self.THROTTLE_TIMEOUT) # don't hurt gmail :(

                self.stdout.write(self.style.SUCCESS(f'Successfully sent {len(messages)} post_event emails.'))

            else:
                self.stdout.write(f'Sent 0 check-in emails.')


    def send_template_test(self, template_name, recipients, action_required = False, context = {}):
        messages = []
        if template_name == 'online_checkin':
            action_required = True
        elif template_name == 'post_event':
            context = {
                'name': '<HackerName>',
                'recruit_url': 'https://ugeorgia.ca1.qualtrics.com/jfe/form/SV_5orFOdgzddQwY74',
                'cert_url': 'https://my.ugahacks.com/static/docs/proof_of_attendance.pdf',
                'desktop_wp_url': 'https://my.ugahacks.com/static/images/ugahacks_6_desktop_wallpaper.png',
                'mobile_wp_url': 'https://my.ugahacks.com/static/images/ugahacks_6_mobile_wallpaper.png',
                'photos_url': 'https://photos.google.com/share/AF1QipPftVrQsQ2hrI0biMNr5qdGpRBx1rn89GHhJR87u4NaelK61_m7DYCnnoc2QkOQOg?key=NDRWeGk4cFRnNzJWdGxvOWJNeGlGY1NEVnd4eVVB'                            
            }

        for email_addr in recipients:
            r_mail = render_mail(f'mails/{template_name}', email_addr, 
                        context, action_required=action_required)
            messages.append(r_mail)

        mail.get_connection().send_messages(messages)
        success_message = f'Successfully sent {len(messages)} ' \
                            + f'non-functional {template_name} emails.'
        self.stdout.write(self.style.SUCCESS(success_message))


    def send_test_online_checkin_emails(self, recipients, template_name):
        messages = []
        reminder_message = f'Remember: functional emails can only be sent to ' \
                            + f'applications with CONFIRMED status.'
        self.stdout.write(reminder_message)
        confirmed_applications = Application.objects.filter(status=Application.CONFIRMED)
                        
        for email_addr in recipients:
            application = confirmed_applications.get(user__email=email_addr)
            messages.append(emails.create_online_checkin_email(application))

        mail.get_connection().send_messages(messages)
        success_message = f'Successfully sent {len(messages)} functional {template_name} emails.'
        self.stdout.write(self.style.SUCCESS(success_message))


    def send_online_checkin_emails_to_all(self):
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
            
            if conf_apps_count >= self.N_CHUNK_NO_THROTTLE:
                self.stdout.write(f'Due to gmail throttling, emails will be sent in batches.')

            messages = []
            for application in confirmed_applications:
                messages.append(emails.create_online_checkin_email(application))
            
            chunked_messages = list(chunk(messages, self.N_CHUNK_NO_THROTTLE))

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
                    self.stdout.write(f'Sleeping for {self.THROTTLE_TIMEOUT}s...')
                    time.sleep(self.THROTTLE_TIMEOUT) # don't hurt gmail :(

                self.stdout.write(self.style.SUCCESS(f'Successfully sent {len(messages)} check-in emails.'))

            else:
                self.stdout.write(f'Sent 0 check-in emails.')