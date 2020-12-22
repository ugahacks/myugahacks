from django.core.management.base import BaseCommand
from django.conf import settings
import csv
from applications import models


class Command(BaseCommand):
    help = 'Prints users that are subscribing to the UGAHacks Newsletter as CSV'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--date', action='store_true', help='sort by submission date')

    def handle(self, *args, **options):
        print('Gathering Newsletter Subscribers...')
        applications = models.Application.objects.filter(hacks_newsletter=True)

        if options['date']:
            applications = applications.order_by('-submission_date')
        
        with open(settings.EXPORT_FILES_URL + 'newsletter_subs.csv', 'w') as newsletter_csv:
            csv_writer = csv.writer(newsletter_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'Email', 'Submission Date'])
            for app in applications:
                res = [app.user.name, app.user.email, app.submission_date.strftime('%m/%d/%Y %H:%M:%S')]
                csv_writer.writerow(res)
        print('Finished gathering Newsletter Subscribers! Check out the csv file called newsletter_subs under /files!')