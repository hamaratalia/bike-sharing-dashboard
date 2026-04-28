# Bike Sharing Data Analysis Dashboard 🚲

## Deskripsi
Proyek ini melakukan analisis mendalam pada "Bike Sharing Dataset" untuk mengungkap pola penyewaan sepeda berdasarkan tren bulanan dan kategori waktu (Jam kerja vs Hari libur). Hasil analisis disajikan dalam dashboard interaktif menggunakan Streamlit.

## Struktur Direktori
- **/dashboard**: Berisi file utama `dashboard.py` dan dataset yang diperlukan.
- **/data**: Berisi dataset mentah (`day.csv` & `hour.csv`).
- **notebook.ipynb**: File analisis data lengkap mulai dari Wrangling hingga Visualisasi.
- **requirements.txt**: Daftar library Python yang dibutuhkan beserta versinya.

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```bash
streamlit run dashboard/dashboard.py
```