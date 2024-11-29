from tensorflow.keras.models import load_model
import joblib

# Muat model dan scaler
model = load_model('model/lstm_model.h5')
scaler_y = joblib.load('model/scaler_Y v1.pkl')

def predict_output(processed_data):
    """
    Melakukan prediksi dengan model yang sudah dimuat.
    - processed_data: Data yang sudah di-preprocess
    - Mengembalikan hasil prediksi dalam skala asli
    """
    # Prediksi menggunakan model
    predictions_scaled = model.predict(processed_data)
    
    # Konversi prediksi ke skala asli
    predictions_original = scaler_y.inverse_transform(predictions_scaled)
    
    return predictions_original
