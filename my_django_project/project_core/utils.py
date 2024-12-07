import os
import numpy as np
import tensorflow as tf
from django.conf import settings
from django.core.files.storage import default_storage

def process_image_and_predict(image_file):
    """
    Handles image processing and prediction using the saved TensorFlow model.
    
    Args:
        image_file: Uploaded image file from request.FILES.
    
    Returns:
        dict: A dictionary with the prediction result or an error message.
    """
    try:
        # Save the uploaded image to the media directory
        image_path = default_storage.save(f'uploads/{image_file.name}', image_file)
        full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        # Load the trained model
        model_path = os.path.join(settings.BASE_DIR, 'llm_model', 'model_new.keras')
        model = tf.keras.models.load_model(model_path)
        
        # Load and preprocess the image
        image = tf.keras.preprocessing.image.load_img(
            full_image_path, target_size=(300, 300), color_mode='grayscale'
        )
        image_array = tf.keras.preprocessing.image.img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
        image_array = image_array / 255.0  # Normalize if needed

        # Make predictions
        prediction = model.predict(image_array)
        predicted_class = np.argmax(prediction, axis=1)

        # Clean up the uploaded image file
        os.remove(full_image_path)

        return {"predicted_class": int(predicted_class[0])}

    except Exception as e:
        return {"error": str(e)}
