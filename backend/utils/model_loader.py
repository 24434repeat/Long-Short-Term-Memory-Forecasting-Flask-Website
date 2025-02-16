import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import traceback
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMModelLoader:
    def __init__(self, model_path, input_size=3, hidden_size=64, num_layers=2, output_size=8, dropout_rate=0.2):
        """
        Initialize LSTM model loader with predefined architecture and business parameters
        
        Args:
            model_path (str): Path to the saved model weights
            input_size (int): Number of input features
            hidden_size (int): Number of LSTM hidden units
            num_layers (int): Number of LSTM layers
            output_size (int): Number of output timesteps
            dropout_rate (float): Dropout rate for regularization
        """
        # Business parameters
        self.target_harian = 476190  # Target pendapatan harian dalam rupiah
        self.harga_ternak_besar = 2000  # Harga per ternak besar
        self.harga_ternak_kecil = 1000  # Harga per ternak kecil
        
        # Load model
        try:
            from torch import nn
            
            class AdvancedLSTMForecaster(nn.Module):
                def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.2):
                    super(AdvancedLSTMForecaster, self).__init__()
                    self.hidden_size = hidden_size
                    self.num_layers = num_layers
                    self.lstm = nn.LSTM(input_size=input_size,
                                      hidden_size=hidden_size,
                                      num_layers=num_layers,
                                      batch_first=True,
                                      dropout=dropout_rate)
                    self.fc = nn.Sequential(
                        nn.Linear(hidden_size, 128),
                        nn.BatchNorm1d(128),
                        nn.ReLU(),
                        nn.Dropout(dropout_rate),
                        nn.Linear(128, 64),
                        nn.BatchNorm1d(64),
                        nn.ReLU(),
                        nn.Dropout(dropout_rate),
                        nn.Linear(64, output_size)
                    )

                def forward(self, x):
                    h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                    c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                    out, _ = self.lstm(x, (h0, c0))
                    out = self.fc(out[:, -1, :])
                    return out

            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = AdvancedLSTMForecaster(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                output_size=output_size,
                dropout_rate=dropout_rate
            ).to(self.device)
            
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            
            # Initialize scaler with realistic ranges
            self.create_custom_scaler()
            
            logger.info("Model and scaler initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise

    def create_custom_scaler(self):
        """Create custom MinMaxScaler with realistic value ranges"""
        self.scaler = MinMaxScaler()
        dummy_data = np.array([
            [0, 0, 0],  # minimum values
            [1000, 1000, 2000000]  # maximum realistic values
        ])
        self.scaler.fit(dummy_data)
        logger.info("Custom scaler created with realistic ranges")

    def predict_revenue(self, ternak_besar, ternak_kecil, sequence_data):
        """
        Predict revenue based on input parameters
        
        Args:
            ternak_besar (float): Number of large livestock
            ternak_kecil (float): Number of small livestock
            sequence_data (np.array): Historical sequence data
            
        Returns:
            dict: Prediction results including daily predictions and statistics
        """
        try:
            logger.info(f"Starting prediction for: ternak_besar={ternak_besar}, ternak_kecil={ternak_kecil}")
            
            # Calculate current revenue
            current_revenue = float((ternak_besar * self.harga_ternak_besar) + 
                                  (ternak_kecil * self.harga_ternak_kecil))
            logger.info(f"Current revenue calculated: {current_revenue}")
            
            # Prepare sequence data
            normalized_sequence = np.zeros_like(sequence_data)
            for i in range(sequence_data.shape[0]):
                if i == sequence_data.shape[0] - 1:
                    sequence_data[i] = [ternak_besar, ternak_kecil, current_revenue]
                normalized_sequence[i] = self.scaler.transform(sequence_data[i].reshape(1, -1))
            
            # Generate predictions
            model_input = torch.FloatTensor(normalized_sequence).reshape(1, 24, 3).to(self.device)
            with torch.no_grad():
                raw_predictions = self.model(model_input).cpu().numpy()
            
            # Process predictions
            predictions = []
            for pred in raw_predictions[0]:
                if current_revenue > self.target_harian:
                    pred_value = current_revenue * (0.9 + pred * 0.2)
                else:
                    pred_value = current_revenue + (self.target_harian - current_revenue) * pred
                predictions.append(pred_value)
            
            # Format results
            result = self._format_predictions(predictions, current_revenue)
            logger.info("Predictions generated and formatted successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            traceback.print_exc()
            raise Exception(f"Gagal melakukan prediksi: {str(e)}")

    def _format_predictions(self, predictions, current_revenue):
        """Format predictions with business logic and dates"""
        result = {
            'status': 'success',
            'predictions': [],
            'target_harian': self.target_harian,
            'current_revenue': current_revenue
        }
        
        # Get next 8 Tuesday/Thursday dates
        current_date = datetime.now()
        dates = []
        days = []
        
        for i in range(28):
            next_date = current_date + timedelta(days=i)
            if next_date.weekday() in [1, 3]:
                dates.append(next_date.strftime('%Y-%m-%d'))
                days.append('Selasa' if next_date.weekday() == 1 else 'Kamis')
                if len(dates) == 8:
                    break
        
        # Format each prediction
        for pred, date, day in zip(predictions, dates, days):
            deficit = float(self.target_harian - pred)
            result['predictions'].append({
                'hari': day,
                'tanggal': date,
                'nilai': float(pred),
                'defisit': deficit,
                'status': 'KURANG' if deficit > 0 else 'TERCAPAI',
                'defisit_rupiah': f"({'- ' if deficit > 0 else '+ '}Rp {abs(deficit):,.0f})"
            })
        
        # Calculate averages
        result['avg_prediction'] = float(np.mean(predictions))
        result['avg_deficit'] = float(self.target_harian - result['avg_prediction'])
        result['status_saat_ini'] = 'KURANG' if result['avg_deficit'] > 0 else 'TERCAPAI'
        
        return result