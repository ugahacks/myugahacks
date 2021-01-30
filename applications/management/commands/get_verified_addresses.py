from django.core.management.base import BaseCommand, CommandError
from applications import models
import csv
import easypost
from time import sleep
from django.conf import settings
from app import settings as app_settings
easypost.api_key = app_settings.EASYPOST_KEY


class Command(BaseCommand):
    help = 'Prints verified addresses for users'

    def handle(self, *args, **options):
        print('Gathering verified addresses...')
        confirmed_applicants = models.Application.objects.filter(status='C')

        verified_applications = []

        for applicant in confirmed_applicants:
            try:
                address = easypost.Address.create(
                    verify=["delivery"],
                    street1=applicant.address_line,
                    street2=applicant.address_line_2,
                    city=applicant.city,
                    state=applicant.state,
                    zip=applicant.zip_code,
                    country="US"
                )
                if address.verifications.delivery.success:
                    verified_applications.append(applicant)
            except easypost.Error as e:
                e_json = e.json_body
                if 'error' in e_json:
                    code = e_json['error']['code'] if 'code' in e_json['error'] else e_json
                    if code == 'RATE_LIMITED':
                        print('rate limited, sleeping...')
                        sleep(60)
                    else:
                        print(code)

        with open(settings.EXPORT_FILES_URL + 'verified_apps.csv', 'w') as verified_csv:
            csv_writer = csv.writer(verified_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Name', 'Email', 'Street', 'City', 'State', 'Zip', 'Country'])
            for app in verified_applications:
                if app.address_line:
                    street = app.address_line + (" " + app.address_line_2 if app.address_line_2 else '')
                    res = [app.user.name, app.user.email, street, app.city, app.state, app.zip_code, "US"]
                    csv_writer.writerow(res)
        print('Finished gathering verified addresses! Check out the csv file called verified_apps under /files!')
