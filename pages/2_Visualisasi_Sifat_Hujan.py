import pandas as pd
import streamlit as st
import plotly.express as px
from utils import category_counts, load_data, safe_cut

st.set_page_config(page_title="Visual Sifat Hujan", page_icon="📊", layout="wide")

st.title("Visual Sifat Hujan")
st.write("Analisis sifat hujan berdasarkan `SH%` dan klasifikasi `SH%`.")

sh_bins = [-1, 30, 50, 84, 115, 150, 200, float('inf')]
sh_labels = [
    '0-30% (Sangat Rendah)',
    '31-50% (Rendah)',
    '51-84% (Kurang Normal)',
    '85-115% (Normal)',
    '116-150% (Lebih Normal)',
    '151-200% (Tinggi)',
    '>200% (Sangat Tinggi)',
]
sh_colors = {
    '0-30% (Sangat Rendah)': '#5D3A1A',
    '31-50% (Rendah)': '#8B4513',
    '51-84% (Kurang Normal)': '#D2B48C',
    '85-115% (Normal)': '#FFD700',
    '116-150% (Lebih Normal)': '#A8E6A1',
    '151-200% (Tinggi)': '#3CB371',
    '>200% (Sangat Tinggi)': '#1B5E20',
}

try:
    df = load_data()
except Exception as exc:
    st.error(f"Data tidak dapat dimuat: {exc}")
    st.stop()

if df.empty:
    st.warning("Data kosong setelah validasi. Tidak ada visualisasi yang dapat ditampilkan.")
    st.stop()

if 'SH%' not in df.columns:
    st.error('Kolom SH% tidak ditemukan dalam data.')
    st.stop()

if df['SH%'].isna().all():
    st.warning('Semua nilai SH% kosong. Tidak ada visualisasi yang dapat ditampilkan.')
    st.stop()

filtered = df.copy()
filtered['SH_category'] = safe_cut(filtered['SH%'], bins=sh_bins, labels=sh_labels)

st.sidebar.header('Filter Visualisasi')
selected_sh = st.sidebar.multiselect('Pilih kategori SH%', sh_labels, default=sh_labels)
filtered = filtered[filtered['SH_category'].isin(selected_sh)].copy()

st.write(f"Menampilkan **{len(filtered):,}** titik setelah filter.")

if filtered.empty:
    st.warning('Tidak ada data yang cocok dengan filter saat ini.')
else:
    legend_html = '<div style="line-height:1.8;">'
    for label in sh_labels:
        legend_html += (
            f"<span style='display:inline-block;width:16px;height:16px;background:{sh_colors[label]};margin-right:8px;border-radius:3px;'></span>{label}<br>"
        )
    legend_html += '</div>'
    st.markdown('### Legenda Kategori SH%', unsafe_allow_html=True)
    st.markdown(legend_html, unsafe_allow_html=True)

    hist_df = category_counts(filtered, 'SH_category', sh_labels)

    fig_sh_hist = px.bar(
        hist_df,
        x='SH_category',
        y='Jumlah',
        color='SH_category',
        color_discrete_map=sh_colors,
        category_orders={'SH_category': sh_labels},
        title='Jumlah Titik per Kategori SH%',
        labels={'SH_category': 'Kategori SH%', 'Jumlah': 'Jumlah Titik'},
        template='plotly_white',
    )

    fig_sh_scatter = px.scatter(
        filtered.sample(n=min(len(filtered), 2000), random_state=1),
        x='SH%',
        y='SHpercentil',
        color='SH_category',
        color_discrete_map=sh_colors,
        category_orders={'SH_category': sh_labels},
        title='SH% vs SHpercentil dengan Klasifikasi SH%',
        labels={'SH%': 'SH%', 'SHpercentil': 'SHpercentil', 'SH_category': 'Kategori SH%'},
        hover_data=['LON', 'LAT', 'CH', 'AnomCH'],
        template='plotly_white',
    )

    fig_sh_anom = px.scatter(
        filtered.sample(n=min(len(filtered), 2000), random_state=2),
        x='SH%',
        y='AnomCH',
        color='SH_category',
        color_discrete_map=sh_colors,
        category_orders={'SH_category': sh_labels},
        title='SH% vs AnomCH dengan Klasifikasi SH%',
        labels={'SH%': 'SH%', 'AnomCH': 'AnomCH', 'SH_category': 'Kategori SH%'},
        hover_data=['LON', 'LAT', 'CH', 'SHpercentil'],
        template='plotly_white',
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_sh_hist, use_container_width=True)
    col2.plotly_chart(fig_sh_scatter, use_container_width=True)
    st.plotly_chart(fig_sh_anom, use_container_width=True)

    stats_df = filtered.groupby('SH_category', observed=False)[['SH%', 'SHpercentil', 'CH', 'AnomCH']].agg(['count', 'mean', 'median'])
    stats_df.columns = ['_'.join(col).strip() for col in stats_df.columns]
    st.markdown('### Statistik Kategori SH%')
    st.dataframe(stats_df.round(2))
