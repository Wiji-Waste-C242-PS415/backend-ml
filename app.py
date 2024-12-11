from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import os
from google.cloud import firestore
from google.cloud import storage
from datetime import datetime
import random

# Inisialisasi Firestore
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
db = firestore.Client()
BUCKET_NAME = "wiji-waste-bucket"

app = Flask(__name__)

# Load model
model = tf.keras.models.load_model('image_classifier_model.h5')
predicted_result = {}

# Preprocessing fungsi
def preprocess_image(image, target_size):
    image = image.resize(target_size)  # Resize gambar ke ukuran target
    if image.mode != "RGB":
            image = image.convert("RGB")
    image = np.array(image)
    image = image / 255.0  # Normalisasi
    image = np.expand_dims(image, axis=0)  # Tambahkan batch dimension
    return image

def get_document_data(collection, doc_id):
    doc_ref = db.collection(collection).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {"error": f"Document '{doc_id}' not found"}

def generate_unique_id():
    date_digit = datetime.now().strftime("%Y%m%d")
    random_digit = random.randint(100, 999)        
    return f"{date_digit}-{random_digit}"

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "WijiWaste API is running..."}), 200

@app.route('/predict', methods=['POST'])
def predict():
    global predicted_result
    if 'file' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        # Buka dan proses gambar
        image = Image.open(file)
        processed_image = preprocess_image(image, target_size=(130, 130))  # Sesuaikan dengan model Anda
        
        # Prediksi
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class])  # Confidence score

        # Respons berdasarkan label
        if predicted_class == 0:
            response_message = "Ini adalah sampah organik. Anda akan mendapatkan 100 poin setiap 1 kg sampah"
        elif predicted_class == 1:
            response_message = "Ini adalah sampah nonorganik. Anda akan mendapatkan 100 poin setiap 1 kg sampah"
        else:
            response_message = "Label tidak dikenali"

        # Reset pointer file untuk upload ke GCS
        file.seek(0)
        image_content = file.read()
        destination_blob_name = f"predictions/{predicted_class}/{file.filename}"

        # Upload ke Google Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(image_content, content_type='image/jpeg')

        doc_id = generate_unique_id()
        '''
        doc_ref = db.collection("predictions").add({
            "prediction_id": doc_id,
            "prediction": int(predicted_class),
            "confidence": confidence,
            "message": response_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "image_url": f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}",
        })
        '''
        db.collection("predictions").document(doc_id).set({
            "prediction_id": doc_id,
            "prediction": int(predicted_class),
            "confidence": confidence,
            "message": response_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "image_url": f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}",
        })
        # Ambil data dari Firestore
        #generated_doc_id = doc_ref[1].id

        # Ambil data dokumen dari Firestore
        document_data = get_document_data("predictions", doc_id)

        # Simpan hasil prediksi di memori
        predicted_result = {
            "prediction_id": doc_id,
            "prediction": int(predicted_class),
            "confidence": confidence,
            "message": response_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "image_url": f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}",
        }
        

        # Kirim respons sebagai JSON
        return jsonify({
            "document_data": document_data,
            "document_id": doc_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
       
@app.route('/predictions', methods=['GET'])
def get_predictions():
    try:
        # Ambil data dari Firestore
        docs = db.collection("predictions").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        predictions = [
            {doc.id: doc.to_dict()} for doc in docs
        ]

        # Kirim respons
        return jsonify(predictions)

    except Exception as e:
        # Tangani error
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Endpoint Get Full Document
@app.route('/predictions/<doc_id>', methods=['GET'])
def get_full_document(doc_id):
    try:
        document_data = get_document_data('predictions', doc_id)
        if "error" in document_data:
            return jsonify({"status": "fail", "message": document_data["error"]}), 404
        return jsonify({"status": "success", "data": document_data}), 200
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route('/predictions/<doc_id>/<field>', methods=['GET'])
def get_document_field(doc_id, field):
    try:
        # Ambil dokumen dari Firestore
        document_data = get_document_data('predictions', doc_id)

        if "error" in document_data:
            return jsonify({"status": "fail", "message": document_data["error"]}), 404

        # Cek apakah field yang diminta ada dalam dokumen
        if field in document_data:
            return jsonify({"status": "success", field: document_data[field]}), 200

        return jsonify({"status": "fail", "message": f"Field '{field}' not found in document '{doc_id}'"}), 404
    except Exception as e:
        return jsonify({"status": "fail", "message": str(e)}), 500


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))