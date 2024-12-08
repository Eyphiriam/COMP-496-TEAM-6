# project_core/views.py
from django.http import JsonResponse
from .forms import ImageUploadForm  # You'll need to create this form
from .models import UploadedImage  # You need a model to save the uploaded images
from .utils import process_image_and_predict  # The function to process and predict using the model
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2
import numpy as np
import tensorflow as tf

def load_model():
    # Load your trained TensorFlow model
    MODEL_PATH = 'llm_model/model_final.keras'  
    model = tf.keras.models.load_model(MODEL_PATH)
    return model

def index(request):
    # Fetch the uploaded images and their results
    images = UploadedImage.objects.all().order_by('-timestamp')
    return render(request, 'core/index.html', {'images': images})

# Upload image view
def upload_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']
        uploaded_image = UploadedImage.objects.create(image=image)

        # Process image and predict after upload
        result = process_image_and_predict(uploaded_image.image.path)
        uploaded_image.result = result  # Store prediction result in the model
        uploaded_image.save()

        return JsonResponse({
            'message': 'Image uploaded and prediction completed!',
            'image_url': uploaded_image.image.url,
            'result': result
        })
    
    return JsonResponse({'error': 'No image uploaded'}, status=400)


from django.http import JsonResponse
from .models import UploadedImage  # Assuming you have this model to store uploaded images and predictions

def view_history(request):
    # Fetch all uploaded images and their results
    images = UploadedImage.objects.all().order_by('-timestamp')  # You can adjust ordering as needed
    
    # Prepare the history data
    history_data = [
        {
            "image_url": image.image.url,  # URL of the uploaded image
            "result": image.result,        # Prediction result for the image
            "timestamp": image.timestamp,  # Timestamp of upload
        }
        for image in images
    ]
    
    # Return the data as a JSON response
    return JsonResponse({'history': history_data})

def show_result(request, image_id):
    uploaded_image = get_object_or_404(UploadedImage, id=image_id)
    
    # Return a JSON response with the result
    return JsonResponse({
        'message': 'Prediction result',
        'image_url': uploaded_image.image.url,
        'result': uploaded_image.result,
    })

def resubmit(request, image_id):
    uploaded_image = get_object_or_404(UploadedImage, id=image_id)
    
    # Reprocess the image and update the result
    result = process_image_and_predict(uploaded_image.image.path)
    uploaded_image.result = result
    uploaded_image.save()
    
    return JsonResponse({
        'message': 'Image reprocessed successfully!',
        'image_url': uploaded_image.image.url,
        'result': result,
    })

@api_view(['POST'])
def process_image(request):
    # Check if the request contains an image
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)

    # Pass the uploaded image to the utility function
    result = process_image_and_predict(request.FILES['image'])

    if "error" in result:
        return Response(result, status=500)

    return Response(result, status=200)