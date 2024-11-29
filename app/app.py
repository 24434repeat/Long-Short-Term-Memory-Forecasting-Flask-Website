from flask import Flask, request, render_template, jsonify
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import pandas as pd
from keras import backend as K

# Inisialisasi Flask
app = Flask(__name__)

def mse(y_true, y_pred):
    return K.mean(K.square(y_true - y_pred))


# Muat model dan scaler
model = load_model('app/models/lstm_model.h5', custom_objects={'mse': mse})
scaler_X = joblib.load('app/models/scaler_X v1.pkl')
scaler_y = joblib.load('app/models/scaler_Y v1.pkl')

# Fungsi untuk preprocessing data input
def preprocess_input(input_data):
    """
    Fungsi untuk melakukan preprocessing pada data input.
    """
    # Normalisasi menggunakan scaler_X
    input_scaled = scaler_X.transform(input_data)
    # Reshape menjadi format yang dapat diterima oleh LSTM
    input_reshaped = input_scaled.reshape((input_scaled.shape[0], input_scaled.shape[1], 1))
    return input_reshaped

# Fungsi untuk postprocessing hasil prediksi
def postprocess_output(predictions_scaled):
    """
    Fungsi untuk mengembalikan hasil prediksi ke skala asli.
    """
    # Inverse transform menggunakan scaler_y
    predictions_original = scaler_y.inverse_transform(predictions_scaled)
    return predictions_original

@app.route('/')
def index():
    """
    Halaman utama.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint untuk prediksi.
    """
    try:
        # Dapatkan data input dalam format JSON
        data = request.json  # Data input dalam format JSON
        
        # Ambil jumlah ternak dan tanggal dari data input
        livestock_count = data.get('livestockCount')
        input_date = data.get('inputDate')
        
        # Siapkan data untuk prediksi
        input_data = pd.DataFrame({'livestockCount': [livestock_count]})
        
        # Preprocessing data input
        processed_data = preprocess_input(input_data)
        
        # Prediksi menggunakan model
        predictions_scaled = model.predict(processed_data)
        
        # Postprocessing hasil prediksi
        predictions_original = postprocess_output(predictions_scaled)
        
        # Ubah hasil prediksi menjadi list untuk dikembalikan dalam response
        results = predictions_original.flatten().tolist()
        
        # Kembalikan hasil prediksi dan tanggal input
        return jsonify({'predictions': results, 'inputDate': input_date})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Jalankan aplikasi Flask
    app.run(debug=True)
