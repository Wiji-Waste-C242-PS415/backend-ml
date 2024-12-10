from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)

# Load model
model = tf.keras.models.load_model('models/image_classifier_model.h5')

# Preprocessing fungsi
def preprocess_image(image, target_size):
    image = image.resize(target_size)  # Resize gambar ke ukuran target
    image = np.array(image)
    image = image / 255.0  # Normalisasi
    image = np.expand_dims(image, axis=0)  # Tambahkan batch dimension
    return image


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        # Buka dan proses gambar
        image = Image.open(file)
        processed_image = preprocess_image(image, target_size=(130, 130))  # Sesuaikan dengan model Anda
        
        # Prediksi
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])

        return jsonify({'prediction': int(predicted_class), 'confidence': float(predictions[0][predicted_class])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
