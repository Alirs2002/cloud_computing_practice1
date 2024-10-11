from django.db import models

class request_data(models.Model):  # Use CamelCase for class names
    ID = models.AutoField(primary_key=True) 
    email = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    caption = models.TextField()
    prev_url = models.CharField(max_length=255)
    new_url = models.CharField(max_length=255)

    def __str__(self):
        return self.email  # Return email or any other relevant field
