# -*- coding: utf-8 -*-
# HACKATHON PERSONALIZATION
import os

from django.utils import timezone

HACKATHON_NAME = 'UGAHacks 6'
# What's the name for the application
HACKATHON_APPLICATION_NAME = "UGAHacks 6"
# Hackathon timezone
TIME_ZONE = 'EST'
# This description will be used on the html and sharing meta tags
HACKATHON_DESCRIPTION = "University of Georgia's Hackathon"
# Domain where application is deployed, can be set by env variable
HACKATHON_DOMAIN = 'my.ugahacks.com'
# Hackathon contact email: where should all hackers contact you. It will also be used as a sender for all emails
HACKATHON_CONTACT_EMAIL = 'hello@ugahacks.com'
# Hackathon logo url, will be used on all emails
HACKATHON_LOGO_URL = 'https://my.ugahacks.com/static/img/github-logo.png'

HACKATHON_OG_IMAGE = 'https://my.ugahacks.com/static/img/logo.png'
# (OPTIONAL) Track visits on your website
HACKATHON_GOOGLE_ANALYTICS = 'UA-179127149-1'
# Hotjar Tracking for heatmaps etc. (Integer)
HACKATHON_HOTJAR_ID = 1566634
# (OPTIONAL) Hackathon Twitter user
HACKATHON_TWITTER_ACCOUNT = 'ugahacks/'
# (OPTIONAL) Hackathon Facebook page
HACKATHON_FACEBOOK_PAGE = 'ugahacks/'
# (OPTIONAL) Hackathon YouTube channel
HACKATHON_YOUTUBE_PAGE = 'UCudlu7Tfg7VL7sR5NJzcCnw'
# (OPTIONAL) Hackathon Instagram user
HACKATHON_INSTAGRAM_ACCOUNT = 'ugahacks/'
# (OPTIONAL) Hackathon Medium user
HACKATHON_MEDIUM_ACCOUNT = ''
# (OPTIONAL) Github Repo for this project (so meta)
HACKATHON_GITHUB_REPO = 'https://github.com/ugahacks/myugahacks/'
# (OPTIONAL) Slack Workspace for the event 
HACKATHON_SLACK = 'https://slack.ugahacks.com/'

# (OPTIONAL) Applications deadline
HACKATHON_APP_DEADLINE = timezone.datetime(2021, 2, 4, 23, 59, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) Online Check-in deadline
CHECKIN_DEADLINE = timezone.datetime(2021, 2, 5, 7, 00, tzinfo=timezone.pytz.timezone(TIME_ZONE))
# (OPTIONAL) When to arrive at the hackathon
# HACKATHON_ARRIVE = 'Check-in opens at 5:00 PM and the opening ceremony will be at 6:30 PM on February 5th at the Zell B. Miller Center. ' \
#                    'Further details about the schedule can be found at 6.ugahacks.com. We hope to see you there!'
# (OPTIONAL) When to arrive at the hackathon
# HACKATHON_LEAVE = 'Closing ceremony will be held on Sunday, February 7th at 1:00 PM. ' \
#                   'However the projects expo fair will be held in the morning from 10:00 AM to 1:00 PM.'
# (OPTIONAL) Hackathon event page
HACKATHON_EVENT_PAGE = 'https://6.ugahacks.com/'
# (OPTIONAL) Pre-event packet link
HACKATHON_PRE_EVENT = 'https://6.ugahacks.com/static/media/pre_event_packet.091f31bd.pdf'

# (OPTIONAL) Regex to automatically match organizers emails and set them as organizers when signing up
REGEX_HACKATHON_ORGANIZER_EMAIL = '^.*@ugahacks\.com$'

# (OPTIONAL) Send 500 errors to email while on production mode
HACKATHON_DEV_EMAILS = ['dev-team@ugahacks.com']

# Baggage configuration
BAGGAGE_ENABLED = False
BAGGAGE_PICTURE = False

# Reimbursement configuration
REIMBURSEMENT_ENABLED = True
DEFAULT_REIMBURSEMENT_AMOUNT = 100
CURRENCY = '$'
REIMBURSEMENT_EXPIRY_DAYS = 5
REIMBURSEMENT_REQUIREMENTS = 'You have to submit a project and demo it during the event in order to get reimbursed'
REIMBURSEMENT_DEADLINE = timezone.datetime(2020, 1, 28, 23, 59,
                                           tzinfo=timezone.pytz.timezone(TIME_ZONE))  # Need to confirm time
# Adds Shipping Address to Application for Prizes
DIGITAL_HACKATHON = True

# (OPTIONAL) Max team members. Defaults to 4
TEAMS_ENABLED = True
HACKATHON_MAX_TEAMMATES = 4

# (OPTIONAL) Code of conduct link
# CODE_CONDUCT_LINK = "https://pages.hackcu.org/code_conduct/"

# (OPTIONAL) Slack credentials
# Highly recommended to create a separate user account to extract the token from
SLACK = {
    'team': os.environ.get('SL_TEAM', 'test'),
    # Get it here: https://api.slack.com/custom-integrations/legacy-tokens
    'token': os.environ.get('SL_TOKEN', None)
}

# (OPTIONAL) Logged in cookie
# This allows to store an extra cookie in the browser to be shared with other application on the same domain
# LOGGED_IN_COOKIE_DOMAIN = '.gerard.space'
# LOGGED_IN_COOKIE_KEY = 'hackassistant_logged_in'

# Hardware configuration
HARDWARE_ENABLED = False
# Hardware request time length (in minutes)
HARDWARE_REQUEST_TIME = 15

SLACK_BOT = {
    'id': os.environ.get('SL_BOT_ID', None),
    'token': os.environ.get('SL_BOT_TOKEN', None),
    'channel': os.environ.get('SL_BOT_CHANNEL', None),
    'director1': os.environ.get('SL_BOT_DIRECTOR1', None),
    'director2': os.environ.get('SL_BOT_DIRECTOR2', None)
}

# Can Hackers start a request on the hardware lab?
# HACKERS_CAN_REQUEST = False
