from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView

from django.http import JsonResponse

from workshops.models import Workshop, Attendance
from checkin.models import CheckIn
from meals.models import Meal, Eaten, MEAL_TYPE
from applications.models import Application
from points.models import Points

from sponsors.models import C_TIER_1, C_TIER_2, C_TIER_3, C_COHOST



class ScanningView(TemplateView):

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
        elif type == 'sponsor':
            return sponsor_scan(request)

def workshop_scan(request):
    id = request.POST.get('id', None)
    qr_code = request.POST.get('qrContent', None)
    workshop = Workshop.objects.filter(id=id).first()
    if not workshop.open and not request.user.is_organizer:
        return JsonResponse({
            'status': 403,
            'message': 'This workshop is not open yet or it has ended.'
        }, status=403)
    response, hacker_user = get_user_from_qr(qr_code)
    if response != None:
        return response
    hacker_attended = workshop.attendance_set.filter(user=hacker_user).first()
    if hacker_attended:
        return JsonResponse({
            'status': 409,
            'message': 'This hacker has already been marked for attendance for this workshop!'
        }, status=409)
    attendance = Attendance(workshop=workshop, user=hacker_user)
    attendance.save()
    #Adding points to the hacker for attending the hackathon
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
    qr_code = request.POST.get('qrContent', None)
    meal = Meal.objects.filter(id=id).first()
    if not meal.opened and not request.user.is_organizer:
        return JsonResponse({
            'status': 403,
            'message': 'This meal is not open yet or it has ended. Reach out to an organizer to activate it again'
        }, status=403)
    response, hacker_user = get_user_from_qr(qr_code)
    if response != None:
        return response
    times_hacker_ate = Eaten.objects.filter(meal=meal, user=hacker_user).count()
    if times_hacker_ate >= meal.times:
        return JsonResponse({
            'status': 409,
            'message': f'Warning! Hacker already ate {times_hacker_ate} out of {meal.times} available times!'
        }, status=409)
    eaten = Eaten(meal=current_meal, user=hacker_application.user)
    eaten.save()
    return JsonResponse({
        'status': 200,
        'message': 'Hacker successfully logged for this meal!'
    })
    #CHECK IF RETURNING A MESSAGE FORO THE DIET IS IMPORTANT

def checkin_scan(request):
    participant_qr = request.POST.get('participantQR', None)
    badge_qr = request.POST.get('badgeQR', None)
    if badge_qr is None or badge_qr =='':
        return JsonResponse({
            'status': 404,
            'message': 'The QR code is mandatory!'
        }, status=404)
    user_application = Application.objects.filter(uuid=participant_qr).first()
    if not user_application:
        return JsonResponse({
            'status': 404,
            'message': 'Hacker\'s application is not found'
        }, status=404)
    user_application.checkin()
    checkin = CheckIn()
    checkin.user = request.user
    checkin.application = user_application
    checkin.qr_identifier = badge_qr
    checkin.save()
    return JsonResponse({
        'status': 200,
        'message': 'Hacker checked-in! Good job! '
                   'Nothing else to see here, '
                   'you can move on :D'
    })

def reissue_scan(request):
    participant_qr = request.POST.get('participantQR', None)
    badge_qr = request.POST.get('badgeQR', None)
    if badge_qr is None or badge_qr =='':
        return JsonResponse({
            'status': 404,
            'message': 'The QR code is mandatory!'
        }, status=404)
    user_application = Application.objects.filter(uuid=participant_qr).first()
    if not user_application:
        return JsonResponse({
            'status': 404,
            'message': 'Hacker\'s application is not found'
        }, status=404)
    checkin = CheckIn.objects.get(application=user_application)
    checkin.qr_identifier = badge_qr
    checkin.save()
    return JsonResponse({
        'status': 200,
        'message': 'Hacker re-issued! Good job! '
                   'Nothing else to see here, '
                   'you can move on :D'
    })

def sponsor_scan(request):
    tier = request.user.get_tier()
    #TODO: MOVE THIS DICTIONARY SOMEWHERE ELSE TO BE USED BY WHOLE PROJECT.
    tier_point_values = {
        C_TIER_1: 3,
        C_TIER_2: 5,
        C_TIER_3: 7,
        C_COHOST: 10,
    }
    if not tier:
        return JsonResponse({
            'status': 401,
            'message': 'We cannot verify you as a sponsor. Please contact an organizer.'
        }, status=401)
    response, hacker_user = get_user_from_qr(qr_code)
    if response != None:
        return response
    points = Points.objects.filter(user=hacker_user).first()
    if not points:
        points = Points(user=hacker_user)
    points.add_points(tier_point_values[tier])
    return JsonResponse({
        'status': 200,
        'message': 'Points successfully added to participant!'
    })

def get_user_from_qr(qr_code):
    response = None
    hacker_user = None
    if not qr_code:
        response = JsonResponse({
            'status': 404,
            'message': 'The QR code is not available.'
        }, status=404)
        return (response, hacker_user)
    hacker_checkin = CheckIn.objects.filter(qr_identifier=id).first()
    if not hacker_checkin:
        response = JsonResponse({
            'status': 404,
            'message': 'Invalid QR code!'
        }, status=404)
        return (response, hacker_user)
    hacker_user = hacker_checkin.application.user
    if not hacker_user:
        response = JsonResponse({
            'status': 404,
            'message': 'No user found for this QR code!'
        }, status=404)
    #response == None if hacker_user is found.
    return (response, hacker_user)
