import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from datetime import date

# ─── Konfigurasi Halaman ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)
sns.set_theme(style="whitegrid")

# ─── 1. LOAD & CLEAN DATA ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    day_df  = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")

    day_df["dteday"]  = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

    day_df["yr"]  = day_df["yr"].map({0: 2011, 1: 2012})
    hour_df["yr"] = hour_df["yr"].map({0: 2011, 1: 2012})

    season_map  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {1: "Clear", 2: "Mist", 3: "Light Rain", 4: "Heavy Rain"}

    day_df["season_label"]  = day_df["season"].map(season_map)
    hour_df["season_label"] = hour_df["season"].map(season_map)
    day_df["weather_label"]  = day_df["weathersit"].map(weather_map)
    hour_df["weather_label"] = hour_df["weathersit"].map(weather_map)

    def categorize_time(hr):
        if   5  <= hr <= 10: return "Pagi"
        elif 11 <= hr <= 14: return "Siang"
        elif 15 <= hr <= 18: return "Sore"
        else:                return "Malam"

    hour_df["time_category"] = hour_df["hr"].apply(categorize_time)
    hour_df["Tipe Hari"]     = hour_df["workingday"].map({0: "Hari Libur", 1: "Hari Kerja"})
    return day_df, hour_df

try:
    day_df, hour_df = load_data()
except FileNotFoundError:
    st.error("File 'day.csv' atau 'hour.csv' tidak ditemukan. "
             "Pastikan file berada di folder yang sama dengan dashboard.py")
    st.stop()

# ─── 2. SIDEBAR FILTER ────────────────────────────────────────────────────────
st.sidebar.title("🚲 Filter Data")
st.sidebar.markdown("Gunakan filter di bawah ini untuk menjelajahi data:")

# --- Filter Tanggal (Date Range) ---
min_date = day_df["dteday"].min().date()
max_date = day_df["dteday"].max().date()

st.sidebar.subheader("📅 Rentang Tanggal")
start_date = st.sidebar.date_input(
    "Tanggal Mulai", value=min_date, min_value=min_date, max_value=max_date
)
end_date = st.sidebar.date_input(
    "Tanggal Akhir", value=max_date, min_value=min_date, max_value=max_date
)

if start_date > end_date:
    st.sidebar.error("Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir.")
    st.stop()

# --- Filter Musim (Selectbox) ---
st.sidebar.subheader("🌸 Pilih Musim")
SEASON_OPTIONS = ["Semua Musim", "Spring", "Summer", "Fall", "Winter"]
selected_season = st.sidebar.selectbox(
    "Musim", options=SEASON_OPTIONS, index=0
)

# Jika "Semua Musim" dipilih → tampilkan semua musim
if selected_season == "Semua Musim":
    active_seasons = ["Spring", "Summer", "Fall", "Winter"]
else:
    active_seasons = [selected_season]

# ─── Terapkan filter ke SEMUA dataframe ───────────────────────────────────────
filtered_day = day_df[
    (day_df["dteday"].dt.date >= start_date) &
    (day_df["dteday"].dt.date <= end_date) &
    (day_df["season_label"].isin(active_seasons))
].copy()

filtered_hour = hour_df[
    (hour_df["dteday"].dt.date >= start_date) &
    (hour_df["dteday"].dt.date <= end_date) &
    (hour_df["season_label"].isin(active_seasons))
].copy()

# ─── Helper: warna bar seragam, highlight max ─────────────────────────────────
BASE_COLOR    = "#6BAED6"
HIGHEST_COLOR = "#08519C"

def bar_colors(values):
    """Semua bar warna seragam, kecuali nilai tertinggi yang di-highlight."""
    colors = [BASE_COLOR] * len(values)
    if len(values) > 0:
        colors[list(values).index(max(values))] = HIGHEST_COLOR
    return colors

# ─── 3. MAIN HEADER & METRICS ─────────────────────────────────────────────────
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown(
    "Dashboard ini menyajikan analisis mendalam pola penyewaan sepeda "
    "tahun 2011–2012. **Semua visualisasi** berubah mengikuti filter yang dipilih."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan",   f"{filtered_day['cnt'].sum():,}")
col2.metric("Rata-rata Harian",  f"{int(filtered_day['cnt'].mean()):,}" if not filtered_day.empty else "–")
col3.metric("Penyewa Terdaftar", f"{filtered_day['registered'].sum():,}")
col4.metric("Penyewa Kasual",    f"{filtered_day['casual'].sum():,}")
st.divider()

# ─── 4. ANALISIS TREN UTAMA ───────────────────────────────────────────────────
st.header("📈 Analisis Tren Utama")
tab1, tab2 = st.tabs(["Tren Bulanan (MoM)", "Pola Jam Puncak"])

with tab1:
    st.subheader("Tren Penyewaan Bulanan")
    if filtered_day.empty:
        st.warning("Tidak ada data pada rentang yang dipilih.")
    else:
        monthly = (
            filtered_day
            .groupby(["yr", "mnth"])["cnt"]
            .sum().reset_index()
        )
        fig, ax = plt.subplots(figsize=(12, 5))
        for yr, color in [(2011, "#2196F3"), (2012, "#FF5722")]:
            sub = monthly[monthly["yr"] == yr]
            if not sub.empty:
                ax.plot(sub["mnth"], sub["cnt"], marker="o",
                        color=color, linewidth=2.5, label=str(yr))
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"])
        ax.set_xlabel("Bulan"); ax.set_ylabel("Total Penyewaan")
        ax.legend(title="Tahun"); ax.grid(True, alpha=0.3)
        st.pyplot(fig); plt.close(fig)
    st.info("**Insight:** 2012 meningkat signifikan dari 2011. Puncak penyewaan terjadi bulan 6–9.")

with tab2:
    st.subheader("Kapan Jam Sibuk di Hari Kerja vs Hari Libur?")
    if filtered_hour.empty:
        st.warning("Tidak ada data pada rentang yang dipilih.")
    else:
        hourly_wd = filtered_hour.groupby(["hr","workingday"])["cnt"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.lineplot(data=hourly_wd, x="hr", y="cnt", hue="workingday",
                     palette={0:"#4ECDC4",1:"#FF6B6B"}, marker="o", linewidth=2.5, ax=ax)
        ax.set_xticks(range(0,24)); ax.set_xlabel("Jam (0–23)"); ax.set_ylabel("Rata-rata Penyewaan")
        handles = [mpatches.Patch(color="#FF6B6B",label="Hari Kerja"),
                   mpatches.Patch(color="#4ECDC4",label="Hari Libur")]
        ax.legend(handles=handles, title="Tipe Hari")
        for v,c in [(8,"#FF6B6B"),(17,"#FF6B6B"),(13,"#4ECDC4")]:
            ax.axvline(v, color=c, linestyle="--", alpha=0.4)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig); plt.close(fig)
    st.info("**Insight:** Hari kerja puncak ganda jam 08:00 & 17:00. Hari libur memuncak siang pukul 12:00–15:00.")

st.divider()

# ─── 5. PENYEWAAN PER MUSIM & CUACA (BAR CHART DENGAN WARNA SERAGAM) ──────────
st.header("📊 Penyewaan per Musim & Kondisi Cuaca")
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("Rata-rata Penyewaan per Musim")
    if filtered_day.empty:
        st.warning("Tidak ada data.")
    else:
        s_avg = (filtered_day.groupby("season_label")["cnt"].mean()
                 .reindex(["Spring","Summer","Fall","Winter"]).dropna())
        colors = bar_colors(s_avg.values)
        fig, ax = plt.subplots(figsize=(7,5))
        bars = ax.bar(s_avg.index, s_avg.values, color=colors, edgecolor="white", width=0.6)
        ax.bar_label(bars, fmt="%.0f", padding=3)
        ax.set_xlabel("Musim"); ax.set_ylabel("Rata-rata Penyewaan"); ax.grid(axis="y", alpha=0.3)
        ax.legend(handles=[mpatches.Patch(color=HIGHEST_COLOR,label="Tertinggi"),
                            mpatches.Patch(color=BASE_COLOR,label="Lainnya")], loc="upper left")
        st.pyplot(fig); plt.close(fig)

with col_b2:
    st.subheader("Rata-rata Penyewaan per Kondisi Cuaca")
    if filtered_day.empty:
        st.warning("Tidak ada data.")
    else:
        w_avg = (filtered_day.groupby("weather_label")["cnt"].mean()
                 .sort_values(ascending=False))
        colors = bar_colors(w_avg.values)
        fig, ax = plt.subplots(figsize=(7,5))
        bars = ax.bar(w_avg.index, w_avg.values, color=colors, edgecolor="white", width=0.6)
        ax.bar_label(bars, fmt="%.0f", padding=3)
        ax.set_xlabel("Kondisi Cuaca"); ax.set_ylabel("Rata-rata Penyewaan"); ax.grid(axis="y", alpha=0.3)
        ax.legend(handles=[mpatches.Patch(color=HIGHEST_COLOR,label="Tertinggi"),
                            mpatches.Patch(color=BASE_COLOR,label="Lainnya")], loc="upper right")
        st.pyplot(fig); plt.close(fig)

st.divider()

# ─── 6. EDA LANJUTAN ──────────────────────────────────────────────────────────
st.header("🔍 Eksplorasi Data Lanjutan (EDA)")
tab_e1, tab_e2, tab_e3 = st.tabs([
    "📦 Distribusi & Korelasi",
    "🎻 Pola Waktu (Violin Plot)",
    "📈 Faktor Lingkungan (Scatter Plot)",
])

with tab_e1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribusi Penyewaan per Musim")
        if filtered_day.empty:
            st.warning("Tidak ada data.")
        else:
            avail = [s for s in ["Spring","Summer","Fall","Winter"]
                     if s in filtered_day["season_label"].unique()]
            medians = filtered_day.groupby("season_label")["cnt"].median()
            top_s   = medians.idxmax() if not medians.empty else None
            palette = {s: (HIGHEST_COLOR if s == top_s else BASE_COLOR) for s in avail}
            fig, ax = plt.subplots(figsize=(8,5))
            sns.boxplot(data=filtered_day, x="season_label", y="cnt",
                        order=avail, palette=palette, ax=ax)
            ax.set_xlabel("Musim"); ax.set_ylabel("Jumlah Penyewaan")
            st.pyplot(fig); plt.close(fig)
    with c2:
        st.subheader("Korelasi Variabel Cuaca & Penyewaan")
        if filtered_day.empty:
            st.warning("Tidak ada data.")
        else:
            corr_m = filtered_day[["cnt","temp","hum","windspeed"]].corr()
            fig, ax = plt.subplots(figsize=(8,5))
            sns.heatmap(corr_m, annot=True, fmt=".2f", cmap="RdYlGn",
                        center=0, linewidths=0.5, ax=ax)
            st.pyplot(fig); plt.close(fig)

with tab_e2:
    st.subheader("Distribusi Penyewaan Berdasarkan Kategori Waktu")
    if filtered_hour.empty:
        st.warning("Tidak ada data.")
    else:
        fig, ax = plt.subplots(figsize=(12,6))
        sns.violinplot(data=filtered_hour, x="time_category", y="cnt", hue="Tipe Hari",
                       order=["Pagi","Siang","Sore","Malam"],
                       palette=["#4ECDC4","#FF6B6B"], split=True, inner="quartile", ax=ax)
        ax.set_xlabel("Kategori Waktu"); ax.set_ylabel("Jumlah Penyewaan")
        ax.set_title("Violin Plot: Hari Kerja vs Hari Libur")
        st.pyplot(fig); plt.close(fig)
    st.info("💡 Rentang interkuartil terlebar ada di segmen **Sore** pada Hari Kerja.")

with tab_e3:
    st.subheader("Pengaruh Kondisi Lingkungan terhadap Penyewaan")
    if filtered_day.empty:
        st.warning("Tidak ada data.")
    else:
        fig, axes = plt.subplots(1, 3, figsize=(18,5))
        for i, (x, title) in enumerate([("temp","Temperatur"),("hum","Kelembaban"),("windspeed","Kecepatan Angin")]):
            r = filtered_day[[x,"cnt"]].corr().iloc[0,1]
            sns.regplot(data=filtered_day, x=x, y="cnt", ax=axes[i],
                        scatter_kws={"alpha":0.4,"color":BASE_COLOR},
                        line_kws={"color":"red","linewidth":2})
            axes[i].set_title(f"{title} vs Penyewaan\n(r = {r:.3f})")
            axes[i].set_ylabel("Total Penyewaan")
        plt.tight_layout()
        st.pyplot(fig); plt.close(fig)
    st.info("💡 Temperatur berkorelasi positif kuat. Kelembaban & kecepatan angin berkorelasi negatif.")

st.divider()
st.caption(
    "© Hamara Talia | "
    "Dicoding Data Analysis Project 2026 | Bike Sharing Dataset"
)