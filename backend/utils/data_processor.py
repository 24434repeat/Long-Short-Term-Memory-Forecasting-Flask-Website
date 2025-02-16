import pandas as pd
import os
from datetime import datetime, timedelta
import traceback
import numpy as np

class DataProcessor:
    def __init__(self, excel_path):
        """
        Initialize data processor with Excel file path
        
        Args:
            excel_path (str): Path to the Excel file containing livestock data
        """
        self.excel_path = excel_path
        self.df = None
        self.load_data()

    def create_empty_excel(self):
        """
        Membuat file Excel kosong dengan struktur kolom yang benar
        """
        try:
            # Buat DataFrame kosong dengan kolom yang diperlukan
            empty_df = pd.DataFrame(columns=[
                'Tanggal',
                'Ternak Besar Masuk',
                'Ternak Kecil Masuk',
                'Total Pendapatan'
            ])
            
            # Simpan ke Excel
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            empty_df.to_excel(self.excel_path, index=False)
            return True
        except Exception as e:
            print(f"Error membuat file Excel: {e}")
            return False

    def load_data(self):
        """
        Load data dari file Excel
        """
        try:
            # Cek apakah file exists
            if not os.path.exists(self.excel_path):
                print("File Excel tidak ditemukan. Membuat file baru...")
                if not self.create_empty_excel():
                    raise Exception("Gagal membuat file Excel")
            
            self.df = pd.read_excel(self.excel_path)
            self.df['Tanggal'] = pd.to_datetime(self.df['Tanggal'])
            
            # Pastikan kolom yang diperlukan ada
            required_columns = [
                'Tanggal', 'Ternak Besar Masuk', 
                'Ternak Kecil Masuk', 'Total Pendapatan'
            ]
            
            for col in required_columns:
                if col not in self.df.columns:
                    raise ValueError(f"Kolom yang diperlukan tidak ada: {col}")
        
        except Exception as e:
            print(f"Error loading data: {e}")
            # Buat DataFrame kosong dengan struktur yang benar
            self.df = pd.DataFrame(columns=[
                'Tanggal', 'Ternak Besar Masuk',
                'Ternak Kecil Masuk', 'Total Pendapatan'
            ])

    def save_new_entry(self, ternak_besar, ternak_kecil, total_pendapatan):
        """
        Save a new entry to the Excel file
        """
        try:
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Create new entry
            new_entry = pd.DataFrame({
                'Tanggal': [current_date],
                'Ternak Besar Masuk': [float(ternak_besar)],
                'Ternak Kecil Masuk': [float(ternak_kecil)],
                'Total Pendapatan': [float(total_pendapatan)]
            })
            
            # Load existing data
            if os.path.exists(self.excel_path):
                existing_data = pd.read_excel(self.excel_path)
                # Pastikan format data konsisten
                existing_data['Tanggal'] = pd.to_datetime(existing_data['Tanggal']).dt.strftime('%Y-%m-%d')
                existing_data['Total Pendapatan'] = existing_data['Total Pendapatan'].astype(float)
            else:
                existing_data = pd.DataFrame(columns=new_entry.columns)
            
            # Concat dan sort
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
            updated_data = updated_data.sort_values('Tanggal')
            
            # Simpan ke Excel
            updated_data.to_excel(self.excel_path, index=False)
            
            # Reload data
            self.load_data()
            print("Data berhasil disimpan")
            return True
            
        except Exception as e:
            print(f"Error saving entry: {e}")
            traceback.print_exc()  # Tambahkan ini untuk debug
            return False

    def get_revenue_history(self, days=30):
        """
        Get revenue history for specified number of days
        """
        try:
            # Ensure data is loaded and sorted
            if self.df is None or self.df.empty:
                print("Data kosong, mengembalikan DataFrame kosong")
                return pd.DataFrame(columns=['Tanggal', 'Total_Pendapatan'])
            
            # Convert and clean data
            self.df['Tanggal'] = pd.to_datetime(self.df['Tanggal'])
            self.df['Total Pendapatan'] = pd.to_numeric(self.df['Total Pendapatan'], errors='coerce').fillna(0)
            
            # Sort and filter data
            self.df = self.df.sort_values('Tanggal', ascending=True)
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = self.df[self.df['Tanggal'] >= cutoff_date].copy()
            
            if recent_data.empty:
                print("Tidak ada data dalam rentang waktu yang diminta")
                return pd.DataFrame(columns=['Tanggal', 'Total_Pendapatan'])
            
            # Format data untuk response
            result = pd.DataFrame({
                'Tanggal': recent_data['Tanggal'].dt.strftime('%Y-%m-%d'),
                'Total_Pendapatan': recent_data['Total Pendapatan']
            })
            
            print("Data yang dikirim:", result.to_dict('records'))
            return result
            
        except Exception as e:
            print(f"Error retrieving revenue history: {e}")
            traceback.print_exc()  # Tambahkan ini untuk debug
            return pd.DataFrame(columns=['Tanggal', 'Total_Pendapatan'])

    def clean_existing_data(self):
        """
        Membersihkan dan memformat ulang data Excel yang ada
        """
        try:
            if os.path.exists(self.excel_path):
                # Baca data existing
                df = pd.read_excel(self.excel_path)
                
                # Convert tanggal ke format yang benar
                df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
                
                # Hapus baris dengan tanggal invalid
                df = df.dropna(subset=['Tanggal'])
                
                # Format ulang kolom
                df['Tanggal'] = df['Tanggal'].dt.strftime('%Y-%m-%d')
                df['Ternak Besar Masuk'] = pd.to_numeric(df['Ternak Besar Masuk'], errors='coerce').fillna(0)
                df['Ternak Kecil Masuk'] = pd.to_numeric(df['Ternak Kecil Masuk'], errors='coerce').fillna(0)
                df['Total Pendapatan'] = pd.to_numeric(df['Total Pendapatan'], errors='coerce').fillna(0)
                
                # Simpan kembali data yang sudah bersih
                df.to_excel(self.excel_path, index=False)
                print("Data Excel berhasil dibersihkan")
                
        except Exception as e:
            print(f"Error membersihkan data: {e}")

    def get_sequence_data(self, ternak_besar, ternak_kecil, window_size=24):
        """
        Get sequence data for model input
        """
        try:
            if self.df is None or self.df.empty:
                # If no historical data, create sequence with zeros
                sequence = np.zeros((window_size, 3))
                for i in range(window_size):
                    sequence[i] = [ternak_besar, ternak_kecil, 0]
                return sequence
            
            # Get last window_size records
            recent_data = self.df.tail(window_size).copy()
            
            if len(recent_data) < window_size:
                # Pad with zeros if not enough historical data
                padding = pd.DataFrame({
                    'Ternak Besar Masuk': [0] * (window_size - len(recent_data)),
                    'Ternak Kecil Masuk': [0] * (window_size - len(recent_data)),
                    'Total Pendapatan': [0] * (window_size - len(recent_data))
                })
                recent_data = pd.concat([padding, recent_data], ignore_index=True)
            
            sequence = np.zeros((window_size, 3))
            for i in range(window_size):
                sequence[i] = [
                    ternak_besar if i == window_size-1 else recent_data.iloc[i]['Ternak Besar Masuk'],
                    ternak_kecil if i == window_size-1 else recent_data.iloc[i]['Ternak Kecil Masuk'],
                    recent_data.iloc[i]['Total Pendapatan']
                ]
            
            return sequence
            
        except Exception as e:
            print(f"Error getting sequence data: {e}")
            traceback.print_exc()
            return None