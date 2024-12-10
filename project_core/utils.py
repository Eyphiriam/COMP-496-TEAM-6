import os
import numpy as np
import tensorflow as tf
import tensorflow as keras 
from tensorflow import keras
from django.conf import settings
from django.core.files.storage import default_storage
from tensorflow.keras.utils import load_img, img_to_array



def process_image_and_predict(image_file):
    """
    Handles image processing and prediction using the saved TensorFlow model.
    
    Args:
        image_file: Uploaded image file from request.FILES.
    
    Returns:
        dict: A dictionary with the prediction result or an error message.
    """
    try:
        # Ensure the function is receiving a valid file path
        if not isinstance(image_file, str):
            return {"error": "Expected a file path, got an object with .name"}

        # Load and preprocess the image
        img = load_img(image_file, target_size=(300, 300), color_mode='grayscale')
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize if needed

        # Load the trained model
        model_path = os.path.join(settings.BASE_DIR, 'llm_model', 'model_final.keras')
        model = tf.keras.models.load_model(model_path)

        # Make predictions
        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)

        return {"predicted_class": int(predicted_class[0])}

    except Exception as e:
        return {"error": str(e)}

