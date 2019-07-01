from django.http import HttpResponse
from django.shortcuts import render, render_to_response


def home(request):
    return render(request, 'home.html')
