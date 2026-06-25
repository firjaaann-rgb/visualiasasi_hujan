import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Visual Sifat Hujan", page_icon="📊", layout="wide")

st.title("Visual Sifat Hujan")
st.write("Analisis sifat hujan berdasarkan `SH%` dan klasifikasi `SH%`.")


df = load_data()

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

filtered = df.copy()
filtered['SH_category'] = pd.cut(filtered['SH%'], bins=sh_bins, labels=sh_labels, right=True)

st.sidebar.header('Filter Visualisasi')
selected_sh = st.sidebar.multiselect('Pilih kategori SH%', sh_labels, default=sh_labels)
filtered = filtered[filtered['SH_category'].isin(selected_sh)]

st.write(f"Menampilkan **{len(filtered):,}** titik setelah filter.")

if len(filtered) == 0:
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

    fig_sh_hist = px.bar(
        filtered['SH_category'].value_counts().reindex(sh_labels).reset_index(name='Jumlah'),
        x='index',
        y='Jumlah',
        title='Jumlah Titik per Kategori SH%',
        labels={'index': 'Kategori SH%', 'Jumlah': 'Jumlah Titik'},
        color='index',
        color_discrete_map=sh_colors,
        template='plotly_white',
    )

    fig_sh_scatter = px.scatter(
        filtered.sample(n=min(len(filtered), 2000), random_state=1),
        x='SH%',
        y='SHpercentil',
        color='SH_category',
        category_orders={'SH_category': sh_labels},
        color_discrete_map=sh_colors,
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
        category_orders={'SH_category': sh_labels},
        color_discrete_map=sh_colors,
        title='SH% vs AnomCH dengan Klasifikasi SH%',
        labels={'SH%': 'SH%', 'AnomCH': 'AnomCH', 'SH_category': 'Kategori SH%'},
        hover_data=['LON', 'LAT', 'CH', 'SHpercentil'],
        template='plotly_white',
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_sh_hist, use_container_width=True)
    col2.plotly_chart(fig_sh_scatter, use_container_width=True)
    st.plotly_chart(fig_sh_anom, use_container_width=True)

    st.markdown('### Statistik Kategori SH%')
    st.dataframe(
        filtered.groupby('SH_category')[['SH%', 'SHpercentil', 'CH', 'AnomCH']]
        .agg(['count', 'mean', 'median'])
        .round(2)
        .sort_index()
    )
