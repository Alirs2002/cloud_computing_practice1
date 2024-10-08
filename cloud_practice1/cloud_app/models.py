from django.db import models

# Create your models here.

class request_data(models.Model):
    ID = models.IntegerField(primary_key=True,unique=True)
    email = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    caption = models.TextField()
    prev_url = models.CharField(max_length=255)
    new_url = models.CharField(max_length=255)

    
