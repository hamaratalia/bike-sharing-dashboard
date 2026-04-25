import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Tema Visual
sns.set_theme(style="whitegrid", palette="husl")

# --- 1. LOAD & CLEAN DATA ---
@st.cache_data
def load_data():
    # Asumsi file day.csv dan hour.csv ada di direktori yang sama
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
    # Konversi tipe data
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Mapping
    day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})
    hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})
    
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {1: 'Clear', 2: 'Mist', 3: 'Light Rain', 4: 'Heavy Rain'}
    
    day_df['season_label'] = day_df['season'].map(season_map)
    hour_df['season_label'] = hour_df['season'].map(season_map)
    day_df['weather_label'] = day_df['weathersit'].map(weather_map)
    hour_df['weather_label'] = hour_df['weathersit'].map(weather_map)
    
    # Kategori Waktu
    def categorize_time(hour):
        if 5 <= hour <= 10: return 'Pagi'
        elif 11 <= hour <= 14: return 'Siang'
        elif 15 <= hour <= 18: return 'Sore'
        else: return 'Malam'
        
    hour_df['time_category'] = hour_df['hr'].apply(categorize_time)
    hour_df['Tipe Hari'] = hour_df['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})
    
    return day_df, hour_df

try:
    day_df, hour_df = load_data()
except FileNotFoundError:
    st.error("File 'day.csv' atau 'hour.csv' tidak ditemukan. Pastikan file berada di folder yang sama dengan app.py")
    st.stop()

# --- 2. SIDEBAR INTERAKTIF ---
st.sidebar.title("🚲 Filter Data")
st.sidebar.markdown("Gunakan filter di bawah ini untuk menjelajahi data:")

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=[2011, 2012],
    default=[2011, 2012]
)

selected_season = st.sidebar.multiselect(
    "Pilih Musim",
    options=['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

# Terapkan filter ke dataframe
filtered_day = day_df[(day_df['yr'].isin(selected_year)) & (day_df['season_label'].isin(selected_season))]
filtered_hour = hour_df[(hour_df['yr'].isin(selected_year)) & (hour_df['season_label'].isin(selected_season))]


# --- 3. MAIN DASHBOARD ---
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown("""
Dashboard ini menyajikan analisis mendalam mengenai pola penyewaan sepeda berdasarkan data historis tahun 2011-2012. 
Insight ini berguna untuk optimasi armada dan strategi operasional.
""")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", f"{filtered_day['cnt'].sum():,}")
col2.metric("Rata-rata Harian", f"{int(filtered_day['cnt'].mean()):,}")
col3.metric("Penyewa Terdaftar (Registered)", f"{filtered_day['registered'].sum():,}")
col4.metric("Penyewa Kasual (Casual)", f"{filtered_day['casual'].sum():,}")

st.divider()

# --- 4. EXPLANATORY ANALYSIS (JAWABAN PERTANYAAN BISNIS) ---
st.header("📈 Analisis Tren Utama")

tab1, tab2 = st.tabs(["Tren Bulanan (MoM)", "Pola Jam Puncak"])

with tab1:
    st.subheader("Bagaimana tren penyewaan sepeda sepanjang tahun 2011 vs 2012?")
    
    monthly_trend = day_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=monthly_trend, x='mnth', y='cnt', hue='yr', marker='o', 
                 palette={2011: '#2196F3', 2012: '#FF5722'}, linewidth=2.5, ax=ax)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    ax.legend(title="Tahun")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.info("**Insight:** Terjadi peningkatan signifikan di tahun 2012 dibandingkan 2011. Pola musiman konsisten memuncak pada pertengahan tahun (bulan 6-9).")

with tab2:
    st.subheader("Kapan jam sibuk di Hari Kerja vs Hari Libur?")
    
    hourly_workday = filtered_hour.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=hourly_workday, x='hr', y='cnt', hue='workingday',
                 palette={0: '#4ECDC4', 1: '#FF6B6B'}, marker='o', linewidth=2.5, ax=ax)
    
    ax.set_xticks(range(0, 24))
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.legend(title="Tipe Hari", labels=['Hari Libur', 'Hari Kerja'])
    
    # Garis penanda puncak
    ax.axvline(8, color='#FF6B6B', linestyle='--', alpha=0.5)
    ax.axvline(17, color='#FF6B6B', linestyle='--', alpha=0.5)
    ax.axvline(13, color='#4ECDC4', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.info("**Insight:** Hari kerja memiliki puncak ganda (bimodal) pada jam 08:00 dan 17:00 (aktivitas komuter). Hari libur memuncak di siang hari antara jam 12:00-15:00 (aktivitas rekreasional).")

st.divider()

# --- 5. EXPLORATORY DATA ANALYSIS (EDA) ---
st.header("🔍 Eksplorasi Data Lanjutan (EDA)")

# Membuat 3 Tab agar dashboard tetap rapi
tab_eda1, tab_eda2, tab_eda3 = st.tabs([
    "📊 Distribusi & Korelasi", 
    "🎻 Pola Waktu (Violin Plot)", 
    "📈 Faktor Lingkungan (Scatter Plot)"
])

with tab_eda1:
    col_eda1, col_eda2 = st.columns(2)
    with col_eda1:
        st.subheader("Distribusi Penyewaan per Musim")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=filtered_day, x='season_label', y='cnt', 
                    order=['Spring', 'Summer', 'Fall', 'Winter'], palette='Set2', ax=ax)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Jumlah Penyewaan")
        st.pyplot(fig)

    with col_eda2:
        st.subheader("Korelasi Variabel Cuaca & Penyewaan")
        corr_cols = ['cnt', 'temp', 'hum', 'windspeed']
        corr_matrix = filtered_day[corr_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='RdYlGn', 
                    center=0, linewidths=0.5, ax=ax)
        st.pyplot(fig)

with tab_eda2:
    st.subheader("Distribusi Penyewaan Berdasarkan Kategori Waktu")
    st.markdown("Melihat sebaran dan kepadatan jumlah penyewaan di berbagai waktu.")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    # Menggunakan filtered_hour agar terpengaruh filter sidebar
    sns.violinplot(data=filtered_hour, x='time_category', y='cnt', hue='Tipe Hari',
                   order=['Pagi', 'Siang', 'Sore', 'Malam'],
                   palette=['#4ECDC4', '#FF6B6B'], split=True, inner='quartile', ax=ax)
    
    ax.set_xlabel("Kategori Waktu")
    ax.set_ylabel("Jumlah Penyewaan")
    ax.set_title("Violin Plot: Hari Kerja vs Hari Libur")
    st.pyplot(fig)
    
    st.info("💡 **Insight EDA:** Rentang interkuartil (area tebal) paling lebar ada di segmen **Sore** pada Hari Kerja, menunjukkan tingginya variasi dan volume penyewaan di jam pulang kerja.")

with tab_eda3:
    st.subheader("Pengaruh Kondisi Lingkungan terhadap Penyewaan")
    st.markdown("Hubungan linier antara variabel numerik lingkungan dengan total penyewaan.")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    pairs = [('temp','cnt','Temperatur'),
             ('hum','cnt','Kelembaban'),
             ('windspeed','cnt','Kecepatan Angin')]
             
    for i, (x, y, title) in enumerate(pairs):
        # Hitung korelasi dinamis berdasarkan data yang difilter
        r = filtered_day[[x, y]].corr().iloc[0, 1] if not filtered_day.empty else 0
        
        sns.regplot(data=filtered_day, x=x, y=y, ax=axes[i],
                    scatter_kws={'alpha':0.4, 'color':'#4ECDC4'},
                    line_kws={'color':'red', 'linewidth':2})
        axes[i].set_title(f"{title} vs Penyewaan\n(r = {r:.3f})")
        axes[i].set_ylabel("Total Penyewaan")
        
    plt.tight_layout()
    st.pyplot(fig)
    
    st.info("💡 **Insight EDA:** Temperatur memiliki korelasi positif yang cukup kuat (garis naik), sedangkan kelembaban dan kecepatan angin berkorelasi negatif secara perlahan (garis turun).")

st.divider()

st.caption("© Hamara Talia — Dicoding Data Analysis Project 2026 | Bike Sharing Dataset")
