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
        uploaded_images = request.FILES.getlist('image')  # Get uploaded files
        predictions = []
        last_uploaded_image_path = None

        for uploaded_image in uploaded_images:
            # Save the uploaded image
            uploaded_img = UploadedImage()
            uploaded_img.image.save(uploaded_image.name, uploaded_image, save=True)
            full_path = uploaded_img.image.path  # Get file path
            logger.info(f"File saved at: {full_path}")

            try:
                # Process the image and get the prediction
                result = process_image_and_predict(full_path)
                predictions.append(result["predicted_class"])  # Save class index

                # Save prediction to PredictionHistory
                pred_history = PredictionHistory(
                    predicted_class=result["predicted_class"],
                    predicted_label=result["predicted_label"]
                )
                pred_history.image_path.name = uploaded_img.image.name
                pred_history.save()

                # Update the last uploaded image path
                last_uploaded_image_path = pred_history.image_path.name
            except Exception as e:
                logger.error(f"Error processing {uploaded_image.name}: {str(e)}")

        # Store predictions and last uploaded image path in the session
        request.session['predictions'] = [int(pred) for pred in predictions]
        if last_uploaded_image_path:
            request.session['last_uploaded_image_path'] = last_uploaded_image_path

        # Redirect to results page
        return redirect('results')

    return render(request, 'core/results.html')


def resubmit(request):
    if request.method == 'POST' and request.FILES.getlist('image'):
        uploaded_images = request.FILES.getlist('image')
        predictions = []
        last_uploaded_image_path = None

        for uploaded_image in uploaded_images:
            # For resubmission, treat it as a new upload
            uploaded_img = UploadedImage()
            uploaded_img.image.save(uploaded_image.name, uploaded_image, save=True)
            full_path = uploaded_img.image.path
            logger.info(f"Resubmit: File saved at: {full_path}")

            try:
                result = process_image_and_predict(full_path)
                predictions.append(result["predicted_class"])  # Save class index

                # Save prediction to PredictionHistory
                pred_history = PredictionHistory(
                    predicted_class=result["predicted_class"],
                    predicted_label=result["predicted_label"]
                )
                pred_history.image_path.name = uploaded_img.image.name
                pred_history.save()

                last_uploaded_image_path = pred_history.image_path.name
            except Exception as e:
                logger.error(f"Error processing {uploaded_image.name}: {str(e)}")

        request.session['predictions'] = predictions
        if last_uploaded_image_path:
            request.session['last_uploaded_image_path'] = last_uploaded_image_path

        return redirect('results')

    return JsonResponse({'status': 'error', 'message': 'No image provided for resubmit or invalid request method.'}, status=400)


def results(request):
    predictions = request.session.get('predictions', [])
    last_uploaded_image_path = request.session.get('last_uploaded_image_path')

    uploaded_image_url = None
    if last_uploaded_image_path:
        uploaded_image_url = settings.MEDIA_URL + last_uploaded_image_path

    # Map predictions to labels
    label_map = {0: 'COVID FREE', 1: 'COVID LIKELY'}
    prediction_messages = [label_map[pred] for pred in predictions] if predictions else ["No prediction"]

    # Log data for debugging
    logger.info(f"Session Predictions: {predictions}, Messages: {prediction_messages}")

    return render(request, 'core/results.html', {
        'prediction_messages': prediction_messages,
        'uploaded_image_url': uploaded_image_url
    })


def view_history(request):
    history = PredictionHistory.objects.all().order_by('-timestamp')[:10]
    return render(request, 'core/View_History.html', {'history': history})


@api_view(['POST'])
def process_image(request):
    if 'image' not in request.FILES:
        return JsonResponse({"error": "No image provided"}, status=400)
    image_file = request.FILES['image']

    # Temporary UploadedImage to apply upload_to logic
    uploaded_img = UploadedImage()
    uploaded_img.image.save(image_file.name, image_file, save=True)
    full_temp_path = uploaded_img.image.path

    try:
        result = process_image_and_predict(full_temp_path)
        pred_history = PredictionHistory(
            predicted_class=result["predicted_class"],
            predicted_label=result["predicted_label"],
            timestamp=datetime.now()
        )
        pred_history.image_path.save(image_file.name, image_file, save=True)
        return JsonResponse({"predicted_class": int(result["predicted_class"])}, status=200)
    finally:
        pass


def contact(request):
    return render(request, 'core/contact.html')


def about(request):
    return render(request, 'core/about.html')
