from django.conf import settings


def is_online_hackathon(request): 
	return {'IS_ONLINE_HACKATHON': settings.IS_ONLINE_HACKATHON}