from django.shortcuts import render,HttpResponse
from .models import request_data
import boto3
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import request_data
from .rabbit import store_id_rabbit,consume_id

# Create your views here.
@csrf_exempt
def answer(request):

    if request.method=='POST':
        img = request.FILES.get('image')
        email = request.POST.get("email")
        print(email)
        if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return HttpResponse("please upload a valid picture please")
        

        entity = request_data(email=email,status = "pending" ,  prev_url = img.name)
        entity.save()

        request_id = entity.ID
      
        store_id_rabbit(request_id)


        access_key = "p1acqtur7hl54lhm"
        secret_key = "3d85581f-1434-4f7c-8250-d0c000d7b69b"
        if img.size==0:
            return HttpResponse("fuck you")
        print(f"File name: {img.name}, Size: {img.size}")

        content_file = ContentFile(img.read(), name=img.name)
        img.seek(0)
        
        
        #s3 = boto3.client('s3', aws_access_key_id='p1acqtur7hl54lhm',
         #                 aws_secret_access_key='3d85581f-1434-4f7c-8250-d0c000d7b69b')

        # Upload the file directly to S3
        
        #s3.upload_fileobj(img, 'cloud-computing-practice1-40031022', img.name)
        try:
            path = default_storage.save(img.name, img)
        except Exception as e:
            return HttpResponse(f"Error uploading file: {str(e)}")
        
    
        #full_file_path = "https://storage.c2.liara.space/cloud-computing-practice1-40031022/"+path
        with default_storage.open(path,"rb") as image_path:
            image = image_path.read()
            response = HttpResponse(image, content_type='image/jpeg')
            response['Content-Disposition'] = f'inline; filename="{img.name}"'
       
    
            return response
        
        
   
        
    #return HttpResponse(response)