from tensorflow.keras.models import load_model

# Load model lama
model = load_model('models/image_classifier_model.h5')

# Simpan ulang dalam format baru
model.save('saved_model/')
