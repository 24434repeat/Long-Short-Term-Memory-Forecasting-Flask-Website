import os
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sys
import traceback
from datetime import datetime
import pandas as pd

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom utilities
from utils.model_loader import LSTMModelLoader
from utils.data_processor import DataProcessor

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model_weights.pth')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'Modeldata.xlsx')

# Pastikan folder data ada
data_dir = os.path.join(BASE_DIR, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

# Buat file Excel kosong jika belum ada
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=[
        'Tanggal',
        'Ternak Besar Masuk',
        'Ternak Kecil Masuk',
        'Total Pendapatan'
    ])
    df.to_excel(DATA_PATH, index=False)

# Initialize Flask app
app = Flask(__name__, 
    static_folder='../frontend/static',  # Lokasi folder static
    static_url_path='/static'            # URL path untuk static files
)
CORS(app)  # Enable CORS for all routes

# Initialize model and data processor
try:
    model_loader = LSTMModelLoader(MODEL_PATH)
    data_processor = DataProcessor(DATA_PATH)
    
    # Validasi inisialisasi
    if data_processor.df is None or data_processor.df.empty:
        print("Peringatan: Dataset kosong atau belum diinisialisasi dengan benar")
    
    # Setelah inisialisasi data_processor
    data_processor.clean_existing_data()
    
except Exception as e:
    print(f"Error inisialisasi: {e}")
    traceback.print_exc()
    sys.exit(1)

@app.route('/predict', methods=['POST'])
def predict_revenue():
    """
    Endpoint for revenue prediction
    
    Expected JSON payload:
    {
        "ternak_besar": float,
        "ternak_kecil": float
    }
    """
    try:
        data = request.json
        ternak_besar = float(data.get('ternak_besar', 0))
        ternak_kecil = float(data.get('ternak_kecil', 0))

        # Validasi input
        if ternak_besar < 0 or ternak_kecil < 0:
            raise ValueError("Jumlah ternak tidak boleh negatif")

        # Get sequence data
        sequence_data = data_processor.get_sequence_data(ternak_besar, ternak_kecil)
        if sequence_data is None:
            raise Exception("Gagal mendapatkan data sequence")

        # Make prediction
        result = model_loader.predict_revenue(ternak_besar, ternak_kecil, sequence_data)
        
        # Save entry to Excel with average prediction
        data_processor.save_new_entry(ternak_besar, ternak_kecil, result['avg_prediction'])

        return jsonify(result), 200

    except ValueError as e:
        print(f"Validation error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"Prediction error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/revenue_history', methods=['GET'])
def get_revenue_history():
    """
    Endpoint to retrieve revenue history
    
    Optional query parameter:
    - days: number of days to retrieve history for (default 30)
    """
    try:
        days = int(request.args.get('days', 30))
        history = data_processor.get_revenue_history(days)
        
        return jsonify({
            'status': 'success',
            'history': history.to_dict(orient='records')
        }), 200

    except Exception as e:
        print(f"History retrieval error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/export_data', methods=['GET'])
def export_data():
    """
    Endpoint to export Excel data
    """
    try:
        return send_from_directory(
            os.path.join(BASE_DIR, 'data'), 
            'Modeldata.xlsx', 
            as_attachment=True
        )
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/')
def serve_frontend():
    """
    Route untuk serving halaman frontend
    """
    return send_file('../frontend/index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)