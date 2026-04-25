import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import f_oneway

import warnings
warnings.filterwarnings('ignore')

# ── Konfigurasi Halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# ── Load & Cache Data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    day_df['yr'] = day_df['yr'].map({0: 2011, 1: 2012})
    hour_df['yr'] = hour_df['yr'].map({0: 2011, 1: 2012})
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weather_map = {1: 'Clear', 2: 'Mist', 3: 'Light Rain', 4: 'Heavy Rain'}
    day_df['season_label'] = day_df['season'].map(season_map)
    hour_df['season_label'] = hour_df['season'].map(season_map)
    day_df['weather_label'] = day_df['weathersit'].map(weather_map)
    hour_df['weather_label'] = hour_df['weathersit'].map(weather_map)
    def categorize_time(h):
        if 5 <= h <= 10: return 'Pagi'
        elif 11 <= h <= 14: return 'Siang'
        elif 15 <= h <= 18: return 'Sore'
        else: return 'Malam'
    hour_df['time_category'] = hour_df['hr'].apply(categorize_time)
    return day_df, hour_df

day_df, hour_df = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=80)
    st.title("🎛️ Pusat Kendali")
    st.markdown("---")

    # ── Filter Rentang Waktu ──
    st.subheader("📅 Filter Waktu")
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    st.markdown("---")

    # ── Filter Musim ──
    st.subheader("🌤️ Filter Musim")
    season_options = ['Semua', 'Spring', 'Summer', 'Fall', 'Winter']
    selected_season = st.selectbox("Pilih Musim", season_options)

    st.markdown("---")

    # ── Filter Kondisi Cuaca ──
    st.subheader("🌦️ Filter Cuaca")
    weather_options = ['Semua', 'Clear', 'Mist', 'Light Rain']
    selected_weather = st.selectbox("Pilih Kondisi Cuaca", weather_options)

    st.markdown("---")

    # ── Filter Tipe Hari ──
    st.subheader("📆 Filter Tipe Hari")
    day_type = st.radio("Tipe Hari", ['Semua', 'Hari Kerja', 'Hari Libur'])

    st.markdown("---")
    st.caption("Bike Sharing Dashboard\n© Hamara Talia — Dicoding 2026")

# ── Terapkan Filter ──────────────────────────────────────────────────────────
main_day_df = day_df[
    (day_df["dteday"] >= str(start_date)) &
    (day_df["dteday"] <= str(end_date))
].copy()
main_hour_df = hour_df[
    (hour_df["dteday"] >= str(start_date)) &
    (hour_df["dteday"] <= str(end_date))
].copy()

if selected_season != 'Semua':
    main_day_df = main_day_df[main_day_df['season_label'] == selected_season]
    main_hour_df = main_hour_df[main_hour_df['season_label'] == selected_season]
if selected_weather != 'Semua':
    main_day_df = main_day_df[main_day_df['weather_label'] == selected_weather]
    main_hour_df = main_hour_df[main_hour_df['weather_label'] == selected_weather]
if day_type == 'Hari Kerja':
    main_day_df = main_day_df[main_day_df['workingday'] == 1]
    main_hour_df = main_hour_df[main_hour_df['workingday'] == 1]
elif day_type == 'Hari Libur':
    main_day_df = main_day_df[main_day_df['workingday'] == 0]
    main_hour_df = main_hour_df[main_hour_df['workingday'] == 0]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("🚲 Bike Sharing Analytics Dashboard")
st.markdown(
    f"Menampilkan data dari **{start_date}** hingga **{end_date}** | "
    f"Musim: **{selected_season}** | Cuaca: **{selected_weather}** | Hari: **{day_type}**"
)
st.divider()

# ── METRIC CARDS ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🚴 Total Penyewaan", f"{main_day_df['cnt'].sum():,}")
with col2:
    st.metric("👤 Pengguna Kasual", f"{main_day_df['casual'].sum():,}")
with col3:
    st.metric("📋 Pengguna Terdaftar", f"{main_day_df['registered'].sum():,}")
with col4:
    avg_per_day = main_day_df['cnt'].mean()
    st.metric("📊 Rata-rata/Hari", f"{avg_per_day:,.0f}")

st.divider()

# ── TAB NAVIGATION ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Pertanyaan 1: Tren Bulanan",
    "⏰ Pertanyaan 2: Jam Puncak",
    "🔍 EDA & Distribusi",
    "📊 Analisis Korelasi"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — PERTANYAAN 1: TREN BULANAN
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Pertanyaan 1: Bagaimana tren penyewaan sepeda (Month-over-Month) sepanjang tahun 2012 dibandingkan dengan tahun 2011?")

    monthly_trend = main_day_df.groupby(['yr', 'mnth'])['cnt'].sum().reset_index()
    monthly_trend['mom_change'] = monthly_trend.groupby('yr')['cnt'].pct_change() * 100

    col_a, col_b = st.columns([2, 1])

    with col_a:
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle("Tren Penyewaan Sepeda per Bulan (2011 vs 2012)", fontsize=13, fontweight='bold')

        sns.lineplot(data=monthly_trend, x='mnth', y='cnt', hue='yr', marker='o',
                     palette={2011: '#2196F3', 2012: '#FF5722'}, ax=axes[0], linewidth=2.5)
        axes[0].set_xticks(range(1, 13))
        axes[0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
        axes[0].set_xlabel("Bulan")
        axes[0].set_ylabel("Total Penyewaan")
        axes[0].set_title("Total Penyewaan Bulanan")
        axes[0].grid(True, alpha=0.4)
        axes[0].legend(title="Tahun")

        for yr, color in [(2011, '#2196F3'), (2012, '#FF5722')]:
            subset = monthly_trend[monthly_trend['yr'] == yr]
            for _, row in subset.iterrows():
                axes[0].annotate(f"{row['cnt']/1000:.0f}K",
                                 (row['mnth'], row['cnt']),
                                 textcoords="offset points", xytext=(0, 8),
                                 ha='center', fontsize=7, color=color)

        for yr, color in [(2011, '#2196F3'), (2012, '#FF5722')]:
            subset = monthly_trend[(monthly_trend['yr'] == yr)].dropna(subset=['mom_change'])
            axes[1].bar(subset['mnth'] + (0.2 if yr == 2012 else -0.2),
                        subset['mom_change'], width=0.38, color=color, alpha=0.8, label=str(yr))
        axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
        axes[1].set_xticks(range(1, 13))
        axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'])
        axes[1].set_xlabel("Bulan")
        axes[1].set_ylabel("MoM Change (%)")
        axes[1].set_title("Month-over-Month Change (%)")
        axes[1].legend(title="Tahun")
        axes[1].grid(True, alpha=0.4, axis='y')

        plt.tight_layout()
        st.pyplot(fig)

    with col_b:
        st.markdown("#### 📋 Tabel Agregasi Bulanan")
        pivot_table = monthly_trend.pivot_table(values='cnt', index='mnth', columns='yr', aggfunc='sum')
        pivot_table.index = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][:len(pivot_table)]
        if 2011 in pivot_table.columns and 2012 in pivot_table.columns:
            pivot_table['Growth (%)'] = ((pivot_table[2012] - pivot_table[2011]) / pivot_table[2011] * 100).round(1)
        st.dataframe(pivot_table.style.format({col: "{:,.0f}" for col in pivot_table.columns if col != 'Growth (%)'}
                                               | {'Growth (%)': '{:.1f}%'}), use_container_width=True)

        st.markdown("#### 💡 Insight")
        st.info("""
**Temuan Utama:**
-  Volume penyewaan 2012 **jauh lebih tinggi** dari 2011 di setiap bulannya.
-  Puncak terjadi pada **bulan 6–9** (musim panas/gugur) di kedua tahun.
-  Penurunan terjadi di **akhir/awal tahun** (musim dingin).
-  Pertumbuhan YoY mencapai **50–100%** di beberapa bulan.
        """)

    with st.expander("📖 Penjelasan Lengkap Visualisasi"):
        st.write("""
Grafik pertama menunjukkan perbandingan total penyewaan bulanan antara 2011 (biru) dan 2012 (oranye).
Secara konsisten, 2012 mengungguli 2011 di setiap bulannya, mengindikasikan pertumbuhan bisnis yang solid.

Grafik kedua (MoM Change %) memperlihatkan fluktuasi bulan ke bulan. Kedua tahun menunjukkan lonjakan
positif saat memasuki musim semi dan penurunan di penghujung tahun saat cuaca memburuk.
        """)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PERTANYAAN 2: JAM PUNCAK
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Pertanyaan 2: Pada jam berapa penyewaan sepeda mencapai puncaknya di hari kerja dibandingkan hari libur selama periode 2011–2012?")

    hourly_wday = main_hour_df.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()

    col_a, col_b = st.columns([3, 2])

    with col_a:
        fig, axes = plt.subplots(2, 1, figsize=(11, 9))
        fig.suptitle("Pola Jam Penyewaan Sepeda 2011–2012\nHari Kerja vs Hari Libur",
                     fontsize=13, fontweight='bold')

        sns.lineplot(data=hourly_wday, x='hr', y='cnt', hue='workingday',
                     palette={0: '#4ECDC4', 1: '#FF6B6B'}, marker='o', ax=axes[0], linewidth=2.5)
        axes[0].set_xticks(range(0, 24))
        axes[0].set_xlabel("Jam (0–23)")
        axes[0].set_ylabel("Rata-rata Penyewaan")
        axes[0].set_title("Rata-rata Penyewaan per Jam")
        axes[0].legend(title="Tipe Hari", labels=['Hari Libur', 'Hari Kerja'])
        for x, label in [(8, '08:00'), (17, '17:00')]:
            axes[0].axvline(x, color='#FF6B6B', linestyle='--', alpha=0.5)
            axes[0].text(x + 0.2, axes[0].get_ylim()[1] * 0.9, label, color='#FF6B6B', fontsize=8)
        axes[0].axvline(13, color='#4ECDC4', linestyle='--', alpha=0.5)
        axes[0].text(13.2, axes[0].get_ylim()[1] * 0.9, '13:00', color='#4ECDC4', fontsize=8)
        axes[0].grid(True, alpha=0.4)

        # Violin per kategori waktu
        cat_order = ['Pagi', 'Siang', 'Sore', 'Malam']
        hour_cat = main_hour_df[main_hour_df['time_category'].isin(cat_order)].copy()
        if not hour_cat.empty:
            hour_cat['Tipe Hari'] = hour_cat['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})
            sns.violinplot(data=hour_cat, x='time_category', y='cnt', hue='Tipe Hari',
                           order=cat_order, palette=['#4ECDC4', '#FF6B6B'],
                           split=True, ax=axes[1], inner='quartile')
            axes[1].set_title("Distribusi Penyewaan per Kategori Waktu")
            axes[1].set_xlabel("Kategori Waktu")
            axes[1].set_ylabel("Jumlah Penyewaan")

        plt.tight_layout()
        st.pyplot(fig)

    with col_b:
        st.markdown("#### 📋 Tabel Jam Puncak")
        if not hourly_wday.empty:
            peak_wday = hourly_wday[hourly_wday['workingday'] == 1].nlargest(5, 'cnt')[['hr', 'cnt']]
            peak_wday.columns = ['Jam', 'Rata-rata (Hari Kerja)']
            peak_hol = hourly_wday[hourly_wday['workingday'] == 0].nlargest(5, 'cnt')[['hr', 'cnt']]
            peak_hol.columns = ['Jam', 'Rata-rata (Hari Libur)']
            st.markdown("**Top 5 Jam Sibuk — Hari Kerja**")
            st.dataframe(peak_wday.reset_index(drop=True).style.format({'Rata-rata (Hari Kerja)': '{:.1f}'}),
                         use_container_width=True)
            st.markdown("**Top 5 Jam Sibuk — Hari Libur**")
            st.dataframe(peak_hol.reset_index(drop=True).style.format({'Rata-rata (Hari Libur)': '{:.1f}'}),
                         use_container_width=True)

        st.markdown("#### 💡 Insight")
        st.info("""
**Temuan Utama:**
- **Hari Kerja:** Puncak tajam jam **08:00** (berangkat) & **17:00** (pulang).
- **Hari Libur:** Kurva lonceng landai, puncak **12:00–15:00** (rekreasi).
- Malam hari & dini hari sangat rendah di kedua tipe hari.
- Gap signifikan antara pola komuter vs rekreasi.
        """)

    with st.expander("📖 Penjelasan Lengkap Visualisasi"):
        st.write("""
Grafik pola jam menunjukkan divergensi perilaku yang sangat berbeda:
- **Hari Kerja:** Dua puncak tajam (bimodal) pada jam 08:00 dan 17:00 mencerminkan penggunaan sepeda
  sebagai alat transportasi komuter.
- **Hari Libur:** Satu puncak (unimodal) landai dari pukul 10:00 hingga 16:00 mencerminkan penggunaan
  santai/rekreasional.

Violin plot menunjukkan distribusi penyewaan per kategori waktu, di mana segmen Sore (15–18)
memiliki variabilitas tertinggi pada hari kerja.
        """)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — EDA & DISTRIBUSI
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔍 Exploratory Data Analysis: Distribusi & Statistik")

    subtab_a, subtab_b, subtab_c = st.tabs(["Univariate", "Kategorikal", "Statistik Deskriptif"])

    with subtab_a:
        st.markdown("#### Distribusi Variabel Numerik (Histogram + KDE)")
        num_cols = ['cnt', 'casual', 'registered', 'temp', 'hum', 'windspeed']
        fig, axes = plt.subplots(2, 3, figsize=(15, 9))
        colors = sns.color_palette("husl", 6)
        for i, col in enumerate(num_cols):
            ax = axes[i // 3][i % 3]
            data = main_day_df[col]
            ax.hist(data, bins=25, color=colors[i], alpha=0.65, edgecolor='white', density=True)
            kde_x = np.linspace(data.min(), data.max(), 200)
            kde = stats.gaussian_kde(data) if len(data) > 1 else None
            if kde:
                ax.plot(kde_x, kde(kde_x), color=colors[i], linewidth=2.2)
            ax.set_title(f"{col}\nSkew={data.skew():.2f} | Kurt={data.kurtosis():.2f}", fontsize=10)
            ax.set_xlabel(col)
            ax.set_ylabel("Densitas")
        plt.suptitle("Distribusi Variabel Numerik (Histogram + KDE)", fontsize=13, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("#### Boxplot — Deteksi Outlier")
        fig2, axes2 = plt.subplots(1, 3, figsize=(14, 5))
        for j, col in enumerate(['cnt', 'temp', 'hum']):
            sns.boxplot(y=main_day_df[col], ax=axes2[j], color=colors[j])
            axes2[j].set_title(f"Boxplot: {col}")
        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown("#### Q-Q Plot — Uji Normalitas")
        fig3, axes3 = plt.subplots(2, 3, figsize=(15, 9))
        for i, col in enumerate(num_cols):
            ax = axes3[i // 3][i % 3]
            data = main_day_df[col].dropna()
            if len(data) > 3:
                stats.probplot(data, dist="norm", plot=ax)
                sw_data = data[:200] if len(data) > 200 else data
                _, p = stats.shapiro(sw_data)
                ax.set_title(f"Q-Q Plot: {col}\nShapiro-Wilk p={p:.4f} ({'Normal' if p > 0.05 else 'Non-Normal'})", fontsize=9)
        plt.suptitle("Q-Q Plot & Shapiro-Wilk Normality Test", fontsize=13, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig3)

    with subtab_b:
        st.markdown("#### Frekuensi Kategorikal")
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        sns.countplot(data=main_day_df, x='season_label', ax=axes[0], palette='Set2',
                      order=[x for x in ['Spring','Summer','Fall','Winter'] if x in main_day_df['season_label'].values])
        axes[0].set_title("Frekuensi per Musim")
        sns.countplot(data=main_day_df, x='mnth', ax=axes[1], palette='Blues_d')
        axes[1].set_title("Frekuensi per Bulan")
        avail_weather = [w for w in ['Clear','Mist','Light Rain'] if w in main_day_df['weather_label'].values]
        sns.countplot(data=main_day_df, x='weather_label', ax=axes[2], palette='Set3', order=avail_weather)
        axes[2].set_title("Frekuensi Kondisi Cuaca")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("#### Distribusi Penyewaan per Kategori")
        fig2, axes2 = plt.subplots(1, 3, figsize=(16, 6))
        sns.boxplot(data=main_day_df, x='season_label', y='cnt', ax=axes2[0], palette='Set2',
                    order=[x for x in ['Spring','Summer','Fall','Winter'] if x in main_day_df['season_label'].values])
        axes2[0].set_title("Penyewaan per Musim")
        sns.violinplot(data=main_day_df, x='weather_label', y='cnt', ax=axes2[1], palette='Set3',
                       order=avail_weather)
        axes2[1].set_title("Penyewaan per Cuaca")
        sns.boxplot(data=main_day_df, x='workingday', y='cnt', ax=axes2[2],
                    palette=['#4ECDC4', '#FF6B6B'])
        axes2[2].set_xticklabels(['Hari Libur', 'Hari Kerja'])
        axes2[2].set_title("Penyewaan: Hari Kerja vs Libur")
        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown("#### ANOVA Statistical Testing")
        if len(main_day_df) > 10:
            results = []
            seasons_present = main_day_df['season'].unique()
            if len(seasons_present) > 1:
                groups = [main_day_df[main_day_df['season'] == s]['cnt'].values for s in seasons_present]
                f, p = f_oneway(*groups)
                results.append({"Variabel": "Musim", "F-statistic": f"{f:.4f}", "p-value": f"{p:.6f}",
                                 "Signifikan": "✅ Ya" if p < 0.05 else "❌ Tidak"})
            weathers_present = main_day_df['weathersit'].unique()
            if len(weathers_present) > 1:
                gw = [main_day_df[main_day_df['weathersit'] == w]['cnt'].values for w in weathers_present]
                f2, p2 = f_oneway(*gw)
                results.append({"Variabel": "Kondisi Cuaca", "F-statistic": f"{f2:.4f}", "p-value": f"{p2:.6f}",
                                 "Signifikan": "✅ Ya" if p2 < 0.05 else "❌ Tidak"})
            wd = main_day_df[main_day_df['workingday'] == 1]['cnt'].values
            wh = main_day_df[main_day_df['workingday'] == 0]['cnt'].values
            if len(wd) > 1 and len(wh) > 1:
                f3, p3 = f_oneway(wd, wh)
                results.append({"Variabel": "Hari Kerja vs Libur", "F-statistic": f"{f3:.4f}", "p-value": f"{p3:.6f}",
                                 "Signifikan": "✅ Ya" if p3 < 0.05 else "❌ Tidak"})
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)
                st.caption("α = 0.05. Signifikan berarti ada perbedaan rata-rata penyewaan antar kelompok.")

    with subtab_c:
        st.markdown("#### Statistik Deskriptif Lengkap")
        num_cols_day = ['cnt', 'casual', 'registered', 'temp', 'hum', 'windspeed']
        st.dataframe(main_day_df[num_cols_day].describe().T.style.format("{:.2f}"), use_container_width=True)

        st.markdown("#### Percentile Analysis")
        percs = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
        perc_df = main_day_df[num_cols_day].quantile(percs).T
        perc_df.columns = [f"P{int(p*100)}" for p in percs]
        st.dataframe(perc_df.style.format("{:.2f}"), use_container_width=True)

        st.markdown("#### Variance & Std Dev per Bulan")
        monthly_var = main_day_df.groupby(['yr', 'mnth'])['cnt'].agg(['mean', 'std', 'var']).reset_index()
        monthly_var.columns = ['Tahun', 'Bulan', 'Mean', 'Std Dev', 'Variance']
        st.dataframe(monthly_var.style.format({'Mean': '{:.1f}', 'Std Dev': '{:.1f}', 'Variance': '{:.1f}'}),
                     use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS KORELASI
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📊 Analisis Korelasi & Hubungan Antar Variabel")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("#### Correlation Matrix Heatmap")
        corr_cols = ['cnt', 'casual', 'registered', 'temp', 'atemp', 'hum', 'windspeed', 'season', 'mnth']
        corr_data = main_day_df[corr_cols].corr()
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        fig, ax = plt.subplots(figsize=(8, 7))
        sns.heatmap(corr_data, annot=True, fmt=".2f", cmap='RdYlGn',
                    mask=mask, center=0, ax=ax, linewidths=0.5, annot_kws={"size": 8})
        ax.set_title("Correlation Matrix (day_df)", fontsize=12, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

    with col_b:
        st.markdown("#### Scatter Plot: Hubungan Variabel dengan Penyewaan")
        x_var = st.selectbox("Pilih variabel X:", ['temp', 'hum', 'windspeed', 'atemp'])
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        sns.regplot(data=main_day_df, x=x_var, y='cnt', ax=ax2,
                    scatter_kws={'alpha': 0.4, 'color': '#4ECDC4'},
                    line_kws={'color': 'red', 'linewidth': 2})
        corr_val = main_day_df[[x_var, 'cnt']].corr().iloc[0, 1]
        ax2.set_title(f"{x_var} vs Penyewaan (r={corr_val:.3f})", fontsize=11)
        ax2.set_xlabel(x_var)
        ax2.set_ylabel("Total Penyewaan (cnt)")
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown("#### Pairplot: Hubungan Komprehensif Antar Variabel")
    if len(main_day_df) > 5:
        pair_cols = ['cnt', 'temp', 'hum', 'windspeed', 'season_label']
        sample_df = main_day_df[pair_cols].sample(min(300, len(main_day_df)), random_state=42)
        avail_seasons = [s for s in ['Spring','Summer','Fall','Winter'] if s in sample_df['season_label'].values]
        g = sns.pairplot(sample_df, hue='season_label', hue_order=avail_seasons,
                         plot_kws={'alpha': 0.5}, diag_kind='kde',
                         palette='Set2', height=2.2)
        g.fig.suptitle("Pairplot: cnt, temp, hum, windspeed per Musim", y=1.01, fontsize=12, fontweight='bold')
        st.pyplot(g.fig)
    else:
        st.warning("Data terlalu sedikit untuk membuat pairplot. Perluas rentang filter.")

st.divider()
st.caption("© Hamara Talia — Dicoding Data Analysis Project 2026 | Bike Sharing Dataset")