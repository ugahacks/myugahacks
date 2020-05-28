import uuid
from random import randint

from django.db import IntegrityError
from django.views.generic.base import TemplateView

from django.http import JsonResponse

from user.models import User
from workshops.models import Workshop, Attendance
from checkin.models import CheckIn
from meals.models import Meal, Eaten, MEAL_TYPE
from applications.models import Application
from points.models import Points

from django.contrib.auth.mixins import LoginRequiredMixin


class ScanningView(LoginRequiredMixin, TemplateView):
    login_url = '/user/login/'
    template_name = 'scanning.html'

    def get_context_data(self, **kwargs):
        context = super(ScanningView, self).get_context_data(**kwargs)
        workshops = Workshop.objects.all()
        meals = Meal.objects.all()
        context.update({
            'workshops': workshops,
            'meals': meals,
            'types': MEAL_TYPE
        })
        return context

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type', None)
        if type == 'workshop':
            return workshop_scan(request)
        elif type == 'meal':
            return meal_scan(request)
        elif type == 'checkin':
            return checkin_scan(request)
        elif type == 'reissue':
            return reissue_scan(request)
        elif type == 'view':
            return view_badge_scan(request)
        elif type == 'disable':
            return change_user_active(request, False)
        elif type == 'enable':
            return change_user_active(request, True)
        elif type == 'award':
            return sponsor_scan(request)


def scanning_generate_view(request):
    if request.method == 'GET':
        credentials = []
        count = int(request.GET.get('count', 1))

        if count > 10:
            return JsonResponse({
                'status': 500,
                'message': 'The count in this request is not included or too high. Max. 10'
            }, status=500)

        for x in range(count):
            user = User(
                email='tester' + str(randint(999, 9999999999)) + '@ugahacks.com',
                name='Tester Account'
            )
            user.set_password('password1')
            user.save()

            application = Application(
                user=user,
                origin='test',
                first_timer=True,
                first_ugahacks=True,
                description="I'm a tester account",
                university="University of Georgia",
                degree="Computational Testing"
            )
            application.save()
            credentials.append({
                'participantQr': application.uuid,
                'badgeQr': uuid.uuid4()
            })

        return JsonResponse({
            'status': 200,
            'message': credentials,
        }, status=200)


def workshop_scan(request):
    id = request.POST.get('id', None)
    qr_code = request.POST.get('badgeQR', None)
    response, hacker_user = get_user_from_qr(qr_code)
    if response is not None:
        return response

    workshop = Workshop.objects.filter(id=id).first()
    if not workshop.open and not request.user.is_organizer:
        return JsonResponse({
            'status': 403,
            'message': 'This workshop is not open yet or it has ended.'
        }, status=403)
    hacker_attended = workshop.attendance_set.filter(user=hacker_user).first()
    if hacker_attended:
        return JsonResponse({
            'status': 409,
            'message': 'This hacker has already been marked for attendance for this workshop!'
        }, status=409)
    attendance = Attendance(workshop=workshop, user=hacker_user)
    attendance.save()
    # Adding points to the hacker for attending the hackathon
    points = Points.objects.filter(user=hacker_user).first()
    if not points:
        points = Points(user=hacker_user)
    points.add_points(workshop.points)
    return JsonResponse({
        'status': 200,
        'message': 'Attendance logged!'
    })


def meal_scan(request):
    id = request.POST.get('id', None)
    qr_code = request.POST.get('badgeQR', None)
    response, hacker_user = get_user_from_qr(qr_code)
    if response is not None:
        return response

    meal = Meal.objects.filter(id=id).first()
    if not meal.opened and not request.user.is_organizer:
        return JsonResponse({
            'status': 403,
            'message': 'This meal is not open yet or it has ended. Reach out to an organizer to activate it again'
        }, status=403)
    times_hacker_ate = Eaten.objects.filter(meal=meal, user=hacker_user).count()
    if times_hacker_ate == meal.times:
        return JsonResponse({
            'status': 409,
            'message': f'Warning! Hacker already ate the max number of available times ({times_hacker_ate})!'
        }, status=409)
    eaten = Eaten(meal=meal, user=hacker_user)
    eaten.save()
    user_application = Application.objects.filter(user_id=hacker_user.id).first()
    return JsonResponse({
        'status': 200,
        'message': 'Hacker successfully logged for this meal!',
        'data': {
            'diet': user_application.diet,
            'other_diet': user_application.other_diet
        }
    })


def checkin_scan(request):
    response, user_application = get_application_from_request(request)
    if response is not None:
        return response

    user_application.check_in()
    checkin = CheckIn()
    checkin.user = request.user
    checkin.application = user_application
    checkin.qr_identifier = request.POST.get('badgeQR', None)

    try:
        checkin.save()
    except IntegrityError:
        return JsonResponse({
            'status': 403,
            'message': "User already checked-in!"
        }, status=403)
    return JsonResponse({
        'status': 200,
        'message': 'Hacker checked-in! Good job! Nothing else to see here, you can move on :D'
    })


def reissue_scan(request):
    response, user_application = get_application_from_request(request)
    if response is not None:
        return response

    checkin = CheckIn.objects.get(application=user_application)
    checkin.qr_identifier = request.POST.get('badgeQR', None)
    checkin.save()
    return JsonResponse({
        'status': 200,
        'message': 'Hacker re-issued! Good job! Nothing else to see here, you can move on :D'
    })


def sponsor_scan(request):
    tier_points = request.user.get_tier_value()
    if not tier_points:
        return JsonResponse({
            'status': 401,
            'message': 'We cannot verify you as a sponsor. Please contact an organizer.'
        }, status=401)
    badge_qr = request.POST.get('badgeQR', None)
    response, hacker_user = get_user_from_qr(badge_qr)
    if response is not None:
        return response
    points = Points.objects.filter(user=hacker_user).first()
    if not points:
        points = Points(user=hacker_user)
    points.add_points(tier_points)
    points.save()
    return JsonResponse({
        'status': 200,
        'message': 'Points successfully added to participant!'
    })


def view_badge_scan(request):
    qr_code = request.POST.get('badgeQR', None)
    response, hacker_checkin = get_checkin_from_qr(qr_code)
    if response is not None:
        return response
    user_application = hacker_checkin.application
    user_application_serialized = user_application.serialize()

    # TODO: Move this logic into the user model as a "get_points" method
    points = Points.objects.filter(user=user_application.user).first()
    if not points:
        points = 0
    else:
        points = points.points
    user_application_serialized['user']['points'] = points
    return JsonResponse({
        'status': 200,
        'message': user_application_serialized
    })


def change_user_active(request, active):
    qr_code = request.POST.get('badgeQR', None)
    response, hacker_checkin = get_checkin_from_qr(qr_code, True)
    if response is not None:
        return response

    hacker_checkin.is_active = active
    hacker_checkin.save()

    return JsonResponse({
        'status': 200,
        'message': 'Badge has been ' + ('enabled' if active is True else 'disabled')
    })


def get_user_from_qr(qr_code):
    response, hacker_checkin = get_checkin_from_qr(qr_code)
    if response is not None:
        return response, hacker_checkin
    hacker_user = hacker_checkin.application.user
    if not hacker_user:
        response = JsonResponse({
            'status': 404,
            'message': 'No user found for this QR code!'
        }, status=404)
    # response == None if hacker_user is found.
    return response, hacker_user


def get_application_from_request(request):
    response = None
    participant_qr = request.POST.get('participantQR', None)
    badge_qr = request.POST.get('badgeQR', None)
    if badge_qr is None or badge_qr == '':
        response = JsonResponse({
            'status': 404,
            'message': 'The QR code is mandatory!'
        }, status=404)
    if participant_qr == badge_qr:
        response = JsonResponse({
            'status': 403,
            'message': 'ParticipantQR and BadgeQr should not equal.'
        }, status=403)
    user_application = Application.objects.filter(uuid=participant_qr).first()
    if not user_application:
        response = JsonResponse({
            'status': 404,
            'message': 'Hacker\'s application is not found'
        }, status=404)
    return response, user_application


def get_checkin_from_qr(qr_code, ignore_disabled_badge=False):
    hacker_checkin = None
    response = None
    if not qr_code:
        response = JsonResponse({
            'status': 404,
            'message': 'The QR code is not available.'
        }, status=404)
        return response, hacker_checkin

    hacker_checkin = CheckIn.objects.filter(qr_identifier=qr_code).first()
    if not hacker_checkin:
        response = JsonResponse({
            'status': 404,
            'message': 'Invalid QR code!'
        }, status=404)
        return response, hacker_checkin
    if not hacker_checkin.is_active and not ignore_disabled_badge:
        response = JsonResponse({
            'status': 403,
            'message': 'Badge is disabled.'
        }, status=403)
    return response, hacker_checkin
