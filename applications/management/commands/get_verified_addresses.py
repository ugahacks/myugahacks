from django.core.management.base import BaseCommand, CommandError
from applications import models
import csv
import easypost
from django.conf import settings
from app import settings as app_settings

easypost.api_key = app_settings.EASYPOST_KEY


class Command(BaseCommand):
    help = 'Prints verified addresses for users'

    def handle(self, *args, **options):
        print('Gathering addresses...')
        verified_applications = models.Application.address_verifier.get_verified()

        with open(settings.EXPORT_FILES_URL + 'verified_apps.csv', 'w') as verified_csv:
            csv_writer = csv.writer(verified_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'Email', 'Street', 'City', 'State', 'Zip', 'Country'])
            for app in verified_applications:
                if app.address_line:
                    street = app.address_line + (" " + app.address_line_2 if app.address_line_2 else '')
                    res = [app.user.name, app.user.email, street, app.city, app.state, app.zip_code, "US"]
                    csv_writer.writerow(res)
        print('Finished gathering verified addresses! Check out the csv file called verified_apps under /files!')
