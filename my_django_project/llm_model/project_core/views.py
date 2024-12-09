import os
from datetime import datetime
import numpy as np
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
import tensorflow as tf
from tensorflow.keras.utils import img_to_array
from project_core.utils import process_image_and_predict
from project_core.models import PredictionHistory, UploadedImage
import logging

logger = logging.getLogger(__name__)
tf.get_logger().setLevel('ERROR')

def load_model():
    model_path = os.path.join(settings.BASE_DIR, 'llm_model', 'model_final.keras')
    return tf.keras.models.load_model(model_path)


def index(request):
    latest_prediction = PredictionHistory.objects.first()
    prediction_history = PredictionHistory.objects.all().order_by('-timestamp')
    return render(request, 'core/index.html', {
        'latest_prediction': latest_prediction,
        'prediction_history': prediction_history,
    })

def upload_image(request):
    if request.method == 'POST' and request.FILES.getlist('image'):
        uploaded_images = request.FILES.getlist('image')
        predictions = []

        for uploaded_image in uploaded_images:
            # Save the uploaded file permanently in the uploads directory
            saved_path = default_storage.save(f'uploads/temp_{uploaded_image.name}', uploaded_image)
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)

            # Log file save
            logger.info(f"File saved at: {full_path}")
            
            try:
                # Process the image and make a prediction
                result = process_image_and_predict(full_path)  # Assume result is a dictionary
                if "predicted_class" in result:
                    prediction = result["predicted_class"]
                    predictions.append(prediction)

                    # Save the result and file path to the database
                    PredictionHistory.objects.create(
                        image_path=saved_path,
                        predicted_class=prediction,
                    )
                else:
                    logger.error(f"Invalid prediction result for {uploaded_image.name}: {result}")
                    continue

            except Exception as e:
                # Handle the exception (log it or pass)
                logger.error(f"Error processing {uploaded_image.name}: {result.get('error', 'Unknown error')}")
                continue

        request.session['predictions'] = predictions
        return redirect('results')

    return render(request, 'results.html')


def view_history(request):
    history = PredictionHistory.objects.all().order_by('-timestamp')[:10]
    return render(request, 'core/View_History.html', {'history': history})

def results(request):
    predictions = request.session.get('predictions', [])
    if not predictions:
        prediction = "No prediction"
    else:
        # Suppose 1 means COVID LIKELY and 0 means COVID FREE
        predicted_class = predictions[0]
        if predicted_class == 1:
            prediction = "COVID LIKELY"
        else:
            prediction = "COVID FREE"

    return render(request, 'core/results.html', {'prediction': prediction})



def resubmit(request):
    if request.method == "POST":
        return JsonResponse({'status': 'success', 'message': 'Image resubmitted successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@api_view(['POST'])
def process_image(request):
    if 'image' not in request.FILES:
        return JsonResponse({"error": "No image provided"}, status=400)
    image_file = request.FILES['image']
    temp_path = default_storage.save(f'temp/{image_file.name}', image_file)
    full_temp_path = os.path.join(settings.MEDIA_ROOT, temp_path)
    try:
        prediction = process_image_and_predict(full_temp_path)
        PredictionHistory.objects.create(
            image_path=temp_path,
            predicted_class=prediction,
            timestamp=datetime.now()
        )
        return JsonResponse({"predicted_class": int(prediction)}, status=200)
    finally:
        os.remove(full_temp_path)
