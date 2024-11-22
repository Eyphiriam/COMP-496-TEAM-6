import tensorflow as tf
import os
import numpy as np


model = tf.keras.models.load_model('llm_model/model.keras')  # Update the path
print("Model loaded successfully")



# Process the image
image = tf.keras.preprocessing.image.load_img('Covid1.png', target_size=(300, 300), color_mode='grayscale')  # Adjust size as necessary
image_array = tf.keras.preprocessing.image.img_to_array(image)
image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
image_array = image_array / 255.0  # Normalize if needed

# Use the model to make predictions
prediction = model.predict(image_array)
predicted_class = np.argmax(prediction, axis=1)  # Get the class index with the highest score