from django.core.management.base import BaseCommand
from django.conf import settings
import csv
from applications import models


class Command(BaseCommand):
    help = 'Prints users that have pending draft applications and have not submitted as CSV'

    def handle(self, *args, **options):
        self.stdout.write('Gathering Draft Applications...')
        applications = [app[0] for app in models.Application.objects.all().values_list('user__email')]
        draft_apps = models.DraftApplication.objects.all()

        with open(settings.EXPORT_FILES_URL + 'draft_apps.csv', 'w') as draft_csv:
            csv_writer = csv.writer(draft_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'Email'])
            for draft_app in draft_apps:
                if draft_app.user.email not in applications:
                    res = [draft_app.user.name, draft_app.user.email]
                    csv_writer.writerow(res)
        self.stdout.write(self.style.SUCCESS(
            'Finished gathering draft submissions! Check out the csv file called draft_apps under /files!'))
