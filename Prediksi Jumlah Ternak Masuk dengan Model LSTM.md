# Prediksi Jumlah Ternak Masuk dengan Model LSTM pada pasar hewan selagalas mataram


[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Naereen/badges)

Website ini merupakan implementasi dari penelitian prediksi jumlah ternak masuk ke pasar hewan Selagalas, Mataram menggunakan model Long Short-Term Memory (LSTM). Sistem ini bertujuan untuk membantu pengelola pasar hewan dalam merencanakan jumlah ternak masuk berdasarkan data historis.

## Features

✅ Prediksi jumlah ternak masuk berdasarkan data historis.
✅ Visualisasi data dalam bentuk grafik jumlah ternak yang masuk setiap Selasa & Kamis.
✅ Input, edit, dan hapus data secara dinamis dalam database excel.
✅ Implementasi model LSTM untuk memproses data time series.
✅ Integrasi antara backend (Flask) dan frontend (HTML, CSS, JS).

# 📂 Struktur folder
```
/backend
│── models/                  # Folder untuk model machine learning
│   ├── config.json          # Konfigurasi model
│   ├── model_weights.pth    # Bobot model LSTM
│   ├── scaler_params.pth    # Parameter normalisasi
│── data/                     # Folder penyimpanan dataset
│   ├── model_data.xlsx      # Data historis ternak
│── utils/                    # Utility scripts untuk pemrosesan data
│   ├── data_processor.py    # Skrip preprocessing data
│   ├── model_loader.py      # Skrip untuk memuat model
│── app.py                    # File utama backend Flask

/frontend
│── static/                   # File statis frontend
│   ├── css/
│   │   ├── style.css         # Styling website
│   ├── js/
│   │   ├── app.js           # Skrip utama frontend
│── index.html                # File utama frontend
│
/venv
│── requirements .txt
```

# ⚙️ Instalasi Penggunaan

## 1. Setup Environment
```
* python -m venv venv
* source venv/bin/activate  # Mac/Linux
* venv\Scripts\activate  # Windows
```
## 2. Install Dependencies
```
pip install -r requirements.txt
```
## 3.Menjalankan Backend
```
python backend/app.py
```
# 🚀 Tech
* Backend: Flask, PyTorch
* Machine Learning: LSTM Model
* Database: Excel
* Frontend: HTML, CSS, JavaScript

# 📩 Kontak

Jika ada pertanyaan atau ingin berkontribusi, silakan hubungi:
📧 Email: jihadakbar425@gmail.com
📌 GitHub: jihadakbar/(24434repeat)

# Credit 
Jihad Akbar
