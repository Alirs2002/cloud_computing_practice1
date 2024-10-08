from django.shortcuts import render,HttpResponse
from .models import request_data
from rest_framework.response import Response

# Create your views here.
def answer(request):

    if request.method=='POST':
        img = request.FILES.get('image')

        if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return HttpResponse("please upload a valid picture please")

    return HttpResponse("fuck you javadi")