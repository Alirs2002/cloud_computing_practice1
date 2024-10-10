from django.shortcuts import render,HttpResponse
from .models import request_data
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def answer(request):

    if request.method=='POST':
        img = request.FILES.get('image')

        if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return HttpResponse("please upload a valid picture please")

    return HttpResponse(img.name)