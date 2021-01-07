from django.core.management.base import BaseCommand
from django.conf import settings
import csv
from applications import models


class Command(BaseCommand):
    help = 'Prints users that wanted to attend UGAHacks 6 in person as CSV'

    def handle(self, *args, **options):
        self.stdout.write('Gathering In-person submissions...')
        applications = models.Application.objects.filter(attendance_type='In-person')
        
        with open(settings.EXPORT_FILES_URL + 'in_person_apps.csv', 'w') as in_person_csv:
            csv_writer = csv.writer(in_person_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'Email'])
            for app in applications:
                res = [app.user.name, app.user.email]
                csv_writer.writerow(res)
        self.stdout.write(self.style.SUCCESS('Finished gathering In-person submissions! Check out the csv file called in_person_apps under /files!'))