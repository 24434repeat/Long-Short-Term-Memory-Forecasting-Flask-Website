import joblib

# Muat scaler
scaler_X = joblib.load('model/scaler_X v1.pkl')

def preprocess_input(input_data):
    """
    Preprocess data input:
    - Normalisasi menggunakan scaler_X
    - Reshape menjadi format yang sesuai untuk LSTM
    """
    # Normalisasi input menggunakan scaler_X
    input_scaled = scaler_X.transform(input_data)
    
    # Reshape data menjadi format [samples, timesteps, features]
    input_reshaped = input_scaled.reshape((input_scaled.shape[0], input_scaled.shape[1], 1))
    
    return input_reshaped
