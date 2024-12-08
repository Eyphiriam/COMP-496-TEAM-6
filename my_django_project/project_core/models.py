from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')  # This saves images in the 'uploads/' directory under MEDIA_ROOT
    result = models.CharField(max_length=50, null=True, blank=True)  # Prediction result (e.g., 'COVID-19 Positive', 'Negative')
    timestamp = models.DateTimeField(auto_now_add=True)  # Time when the image was uploaded

    def __str__(self):
        return f"{self.image.name} - {self.result}"

class PredictionHistory(models.Model):
    image_path = models.CharField(max_length=255)
    predicted_class = models.IntegerField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Prediction {self.id} - Class {self.predicted_class} at {self.timestamp}"