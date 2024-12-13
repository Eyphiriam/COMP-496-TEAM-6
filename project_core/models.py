# project_core/models.py
from django.db import models
import os
from datetime import datetime

def upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"uploads/{base}_{timestamp}{ext}"

class UploadedImage(models.Model):
    image = models.ImageField(upload_to=upload_to)  # Save images with a human-readable timestamp
    result = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically records the upload time

    def __str__(self):
        return f"{self.image.name} - {self.result}"
    
class PredictionHistory(models.Model):
    predicted_class = models.IntegerField()  # Store class index (0 or 1)
    predicted_label = models.CharField(
        max_length=20,
        null=True,  # Allow null values for existing rows
        blank=True  # Allow blank values in forms
    )  # Store the label ('COVID FREE' or 'COVID LIKELY')
    image_path = models.ImageField(upload_to='uploads/')
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically add timestamp

    def __str__(self):
        return f"{self.predicted_label} - {self.timestamp}"