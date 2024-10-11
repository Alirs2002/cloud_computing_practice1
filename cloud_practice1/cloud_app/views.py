from django.shortcuts import render,HttpResponse
from .models import request_data
import boto3
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.
@csrf_exempt
def answer(request):

    if request.method=='POST':
        img = request.FILES.get('image')
        email = request.POST.get("email")
        print(email)
        if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return HttpResponse("please upload a valid picture please")
        #fs = FileSystemStorage()
        #filename = fs.save(img.name,img)
        #file_path = fs.url(filename)

        access_key = "p1acqtur7hl54lhm"
        secret_key = "3d85581f-1434-4f7c-8250-d0c000d7b69b"
        if img.size==0:
            return HttpResponse("fuck you")
        print(f"File name: {img.name}, Size: {img.size}")

        content_file = ContentFile(img.read(), name=img.name)
        img.seek(0)
            # Save the file using default_storage
        
        #s3 = boto3.client('s3', aws_access_key_id='p1acqtur7hl54lhm',
         #                 aws_secret_access_key='3d85581f-1434-4f7c-8250-d0c000d7b69b')

        # Upload the file directly to S3
        
        #s3.upload_fileobj(img, 'cloud-computing-practice1-40031022', img.name)
        try:
            path = default_storage.save(img.name, img)
        except Exception as e:
            return HttpResponse(f"Error uploading file: {str(e)}")
    return HttpResponse(email)