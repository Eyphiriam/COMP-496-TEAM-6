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
    image_path = models.ImageField(upload_to=upload_to)  # Use the same file naming scheme
    predicted_class = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction at {self.timestamp} - Class: {self.predicted_class}"
