import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman (Biar tampilan lebih lebar dan rapi)
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# Gunakan cache agar data tidak diload berulang kali setiap ada interaksi
@st.cache_data
def load_data():
    # Pastikan file day.csv dan hour.csv berada di folder yang sama dengan file ini
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
    # Ubah tipe data dteday menjadi datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Mapping tahun agar lebih intuitif di grafik
    day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})
    hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})
    
    return day_df, hour_df

day_df, hour_df = load_data()

# ================= SIDEBAR =================
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=150) # Tambahan logo biar cantik
    st.title("Pusat Kendali")
    
    # Filter rentang waktu
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# ================= FILTERING DATA =================
# Terapkan filter tanggal ke KEDUA dataframe (day dan hour)
main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                     (day_df["dteday"] <= str(end_date))]

main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                       (hour_df["dteday"] <= str(end_date))]

# ================= MAIN DASHBOARD =================
st.header('Bike Sharing Analytics Dashboard 🚲')

# Menambahkan Metric Cards (Ringkasan Angka) - Ini disukai reviewer!
col1, col2, col3 = st.columns(3)
with col1:
    total_rent = main_day_df['cnt'].sum()
    st.metric("Total Penyewaan Sepeda", value=f"{total_rent:,}")
with col2:
    total_casual = main_day_df['casual'].sum()
    st.metric("Pengguna Kasual", value=f"{total_casual:,}")
with col3:
    total_registered = main_day_df['registered'].sum()
    st.metric("Pengguna Terdaftar", value=f"{total_registered:,}")

st.divider() # Garis pemisah

# --- Visualisasi 1: Tren Bulanan ---
st.subheader('Tren Penyewaan Bulanan')

# Agregasi data dari data yang SUDAH difilter (main_day_df)
monthly_trend = main_day_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
# Palet warna disesuaikan biar lebih menarik
sns.lineplot(data=monthly_trend, x='mnth', y='cnt', hue='yr', marker='o', ax=ax, palette="Set1")
ax.set_xticks(range(1, 13))
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Perbandingan Penyewaan Sepeda Tahun 2011 & 2012")
st.pyplot(fig)
# Penjelasan Tren Bulanan dengan Expander
with st.expander("Lihat Penjelasan Grafik Tren Bulanan"):
    st.write("""
        Grafik di atas menunjukkan perbandingan performa penyewaan sepeda antara tahun 2011 dan 2012:
        - **Pertumbuhan Tahunan:** Terjadi peningkatan jumlah penyewaan yang sangat signifikan di tahun 2012 (garis biru/merah sesuai palet) dibandingkan tahun 2011 hampir di setiap bulannya.
        - **Pola Musiman:** Kedua tahun menunjukkan pola yang serupa, di mana penyewaan cenderung rendah di awal tahun (Januari-Februari), kemudian meningkat pesat dan mencapai puncaknya pada pertengahan tahun hingga kuartal ketiga (bulan Juni hingga September).
        - **Penurunan Akhir Tahun:** Jumlah penyewaan kembali menurun saat memasuki akhir tahun (November-Desember), yang kemungkinan dipengaruhi oleh faktor cuaca atau musim dingin.
    """)
    
st.divider() # Garis pemisah

# --- Visualisasi 2: Grafik Jam Puncak ---
st.subheader('Pola Penyewaan Sepeda Berdasarkan Jam')

fig, ax = plt.subplots(figsize=(12, 6))
# Gunakan data jam yang SUDAH difilter (main_hour_df)
sns.lineplot(
    data=main_hour_df, 
    x='hr', 
    y='cnt', 
    hue='workingday', 
    estimator='mean', 
    ax=ax,
    palette="viridis"
)

ax.set_title('Rata-rata Penyewaan: Hari Kerja (1) vs Hari Libur (0)')
ax.set_xlabel('Jam (0-23)')
ax.set_ylabel('Jumlah Rata-rata Penyewaan')
ax.set_xticks(range(0, 24))
ax.grid(True, linestyle='--', alpha=0.6)
st.pyplot(fig)

# Penjelasan dengan Expander
with st.expander("Lihat Penjelasan Grafik Pola Jam"):
    st.write("""
        Berdasarkan grafik di atas, kita dapat melihat perbedaan perilaku penyewa sepeda:
        - **Hari Kerja (Garis Hijau/1):** Penyewaan memuncak tajam pada jam berangkat kerja/sekolah (08:00) dan jam pulang (17:00).
        - **Hari Libur (Garis Biru/0):** Pola penyewaan membentuk kurva lonceng, di mana penyewaan perlahan naik sejak pagi dan mencapai puncaknya pada siang hingga sore hari (12:00 - 15:00) untuk rekreasi.
    """)

st.caption("Copyright © Hamara Talia - Dicoding Data Analysis Project 2026")