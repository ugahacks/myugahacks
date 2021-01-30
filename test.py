import easypost
from app import settings as app_settings
from time import sleep

easypost.api_key = app_settings.EASYPOST_KEY

for i in range(100):
    try:
        address = easypost.Address.create(
            verify=["delivery"],
            street1='583 windcroft circle NW',
            city='acworth',
            state='ga',
            zip='30101',
            country="US"
        )
        print('success')
    except easypost.Error as e:
        e_json = e.json_body
        if 'error' in e_json:
            code = e_json['error']['code'] if 'code' in e_json['error'] else e_json
            if code == 'RATE_LIMITED':
                print('rate limited, sleeping...')
                sleep(60)
            else:
                print(code)
