from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.storage import default_storage
import tensorflow as tf
import os
from django.conf import settings
import numpy as np

@api_view(['POST'])
def process_image(request):
    # Check if the request contains an image
    if 'image' not in request.FILES:
        return Response({"error": "No image provided"}, status=400)

    # Save the uploaded image
    image_file = request.FILES['image']
    image_path = default_storage.save(f'uploads/{image_file.name}', image_file)

    # Ensure the image path is correct
    full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

    # Load the trained LLM model
    try:
        model = tf.keras.models.load_model('path/to/your/cvd_cnn.keras')  # Update the path
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        return Response({"error": "Model loading failed"}, status=500)

    # Process the image
    image = tf.keras.preprocessing.image.load_img(full_image_path, target_size=(300, 300), color_mode='grayscale')  # Adjust size as necessary
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    image_array = image_array / 255.0  # Normalize if needed

    # Use the model to make predictions
    prediction = model.predict(image_array)
    predicted_class = np.argmax(prediction, axis=1)  # Get the class index with the highest score

    # Return the prediction in the API response
    return Response({"predicted_class": int(predicted_class[0])}, status=200)
