import os
import numpy as np
import tensorflow as tf
import tensorflow as keras 
from tensorflow import keras
from django.conf import settings
from django.core.files.storage import default_storage
from tensorflow.keras.utils import load_img, img_to_array
import cv2
import logging
# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load the model once during server startup

MODEL_PATH = os.path.join(settings.BASE_DIR, 'llm_model', 'model_final.keras')
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")

def load_and_preprocess_image(image_path, img_size=(300, 300)):
    # Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")
    
    # Resize image
    img_resized = cv2.resize(img, img_size, interpolation=cv2.INTER_NEAREST)
    
    # Reshape to (1, 300, 300, 1) and convert to float32
    img_reshaped = img_resized.reshape(1, img_size[0], img_size[1], 1).astype('float32')
    
    # Normalize pixel values to range [0, 1]
    img_normalized = img_reshaped / 255.0
    
    return img_normalized

def process_image_and_predict(image_path):
    # Load and preprocess the image
    processed_image = load_and_preprocess_image(image_path)

    # Make predictions
    predictions = model.predict(processed_image)
    predicted_class = np.argmax(predictions, axis=1)[0]  # Get class index (0 or 1)

    # Map prediction to label
    label_map = {0: 'COVID FREE', 1: 'COVID LIKELY'}
    predicted_label = label_map.get(predicted_class, "Unknown")

    # Log predictions for debugging
    logger.info(f"Predictions: {predictions}, Predicted Class: {predicted_class}, Predicted Label: {predicted_label}")

    return {
        "predicted_class": predicted_class,
        "predicted_label": predicted_label
    }
