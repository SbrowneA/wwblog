from django.shortcuts import render
from django.http import HttpResponse
from wwblog.settings import BASE_DIR


def index(request):
    print(f"{BASE_DIR}")
    return HttpResponse(f"{BASE_DIR}")
