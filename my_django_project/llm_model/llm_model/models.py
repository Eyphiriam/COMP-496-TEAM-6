from django.db import models


class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/')  # Adjust 'uploads/' as needed
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.imag