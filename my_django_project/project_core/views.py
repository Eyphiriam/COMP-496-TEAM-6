# project_core/views.py
from django.shortcuts import render
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
from django.core.files.storage import default_storage
import os
from django.conf import settings
from datetime import datetime
from .models import PredictionHistory  
# Simulated database for storing history
history_db = []

def load_model():
    # Load your trained TensorFlow model
    MODEL_PATH = 'llm_model/model_final.keras'  
    model = tf.keras.models.load_model(MODEL_PATH)
    return model

def index(request):
    # Get the latest prediction result
    prediction = PredictionHistory.objects.first()  # Latest prediction
    # Get all prediction history
    prediction_history = PredictionHistory.objects.all().order_by('-timestamp')  # Optional: Limit results to show top N
    return render(request, 'core/index.html', {
        'prediction': prediction,
        'prediction_history': prediction_history,
    })


# Upload image view
def upload_image(request):
    result = None
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


def view_history(request):
    # Get the latest prediction result (or all predictions)
    history = PredictionHistory.objects.all().order_by('-timestamp')[:10]  # Show the last 10 predictions

    # Pass the history to the template
    return render(request, 'core/index.html', {'history': history})

def results(request, image_id):
    # Fetch the image record based on image_id
    image = get_object_or_404(UploadedImage, id=image_id)
    # Perform processing or pass the image to the template
    return render(request, 'core/index.html', {'image': image})

def resubmit(request):
    if request.method == "POST":
        # Handle the resubmission logic
        return JsonResponse({'status': 'success', 'message': 'Image resubmitted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

#model used to process the image
@api_view(['POST'])
def process_image(request):
    # Check if the request contains an image
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)
    
    image_file = request.FILES['image']
    image_path = default_storage.save(f'uploads/{image_file.name}', image_file)
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

  # Load the model
    model_path = os.path.join(settings.BASE_DIR, 'llm_model', 'model_final.keras')
    try:
        model = tf.keras.models.load_model(model_path)
    except Exception as e:
        return Response({"error": f"Model loading failed: {e}"}, status=500)
   # Process the image for prediction
    image = tf.keras.preprocessing.image.load_img(full_image_path, target_size=(300, 300), color_mode='grayscale')
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = image_array / 255.0

    # Make prediction
    prediction = model.predict(image_array)
    predicted_class = np.argmax(prediction, axis=1)

    # Save the result to history (optional)
    PredictionHistory.objects.create(image_path=image_path, predicted_class=predicted_class[0], timestamp=datetime.now())

    return Response({"predicted_class": int(predicted_class[0])}, status=200)
