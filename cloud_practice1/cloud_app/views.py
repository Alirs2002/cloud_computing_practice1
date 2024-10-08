from django.shortcuts import render,HttpResponse
from .models import request_data

# Create your views here.
def answer(request):
    return HttpResponse("fuck you javadi")