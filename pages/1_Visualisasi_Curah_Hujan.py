import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
from utils import category_counts, load_data, safe_cut

st.set_page_config(page_title="Visual Curah Hujan", page_icon="🗺️", layout="wide")

st.title("Visual Curah Hujan")
st.write("Peta interaktif menampilkan titik-titik curah hujan dengan klasifikasi `CH`.")

ch_bins = [-1, 10, 20, 50, 75, 100, 150, 200, 300, float('inf')]
ch_labels = [
    '0-10 mm (Sangat Rendah)',
    '10-20 mm (Rendah)',
    '20-50 mm (Menengah Rendah)',
    '50-75 mm (Menengah)',
    '75-100 mm (Menengah Atas)',
    '100-150 mm (Cukup Tinggi)',
    '150-200 mm (Tinggi)',
    '200-300 mm (Sangat Tinggi)',
    '>300 mm (Ekstrem)',
]
ch_colors = {
    '0-10 mm (Sangat Rendah)': '#8B0000',
    '10-20 mm (Rendah)': '#FF4500',
    '20-50 mm (Menengah Rendah)': '#FFA500',
    '50-75 mm (Menengah)': '#FFB347',
    '75-100 mm (Menengah Atas)': '#FFD700',
    '100-150 mm (Cukup Tinggi)': '#FFF8B7',
    '150-200 mm (Tinggi)': '#98FB98',
    '200-300 mm (Sangat Tinggi)': '#32CD32',
    '>300 mm (Ekstrem)': '#006400',
}

try:
    df = load_data()
except Exception as exc:
    st.error(f"Data tidak dapat dimuat: {exc}")
    st.stop()

if df.empty:
    st.warning("Data kosong setelah validasi. Periksa sumber data.")
    st.stop()

if 'CH' not in df.columns:
    st.error('Kolom CH tidak ditemukan dalam data.')
    st.stop()

if df['CH'].isna().all():
    st.warning('Semua nilai CH kosong. Tidak ada visualisasi yang dapat ditampilkan.')
    st.stop()

if df['LAT'].isna().all() or df['LON'].isna().all():
    st.warning('Koordinat lokasi tidak lengkap. Peta tidak dapat ditampilkan.')

df['CH_category'] = safe_cut(df['CH'], bins=ch_bins, labels=ch_labels)

min_ch, max_ch = float(df['CH'].min()), float(df['CH'].max())
ch_range = st.sidebar.slider(
    'Rentang CH untuk ditampilkan',
    min_value=min_ch,
    max_value=max_ch,
    value=(min_ch, min(max_ch, min_ch + 120.0)),
    step=1.0,
)
map_style = st.sidebar.radio('Jenis peta', ['Heatmap', 'Marker cluster'])
marker_sample = st.sidebar.slider('Jumlah titik marker', 200, 1500, 900, step=100)

selected = df.query('CH >= @ch_range[0] and CH <= @ch_range[1]').copy()
selected_count = len(selected)
st.write(f"Menampilkan **{selected_count:,}** titik yang sesuai filter.")

if selected_count == 0:
    st.warning('Tidak ada data yang cocok untuk filter saat ini.')
else:
    center_lat = float(selected['LAT'].mean())
    center_lon = float(selected['LON'].mean())
    map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles='CartoDB positron')

    if map_style == 'Heatmap':
        heat_data = selected[['LAT', 'LON', 'CH']].values.tolist()
        HeatMap(heat_data, min_opacity=0.3, radius=15, blur=20, max_val=max_ch).add_to(map_obj)
    else:
        sample = selected.sort_values('CH', ascending=False).head(marker_sample)
        cluster = MarkerCluster()
        for _, row in sample.iterrows():
            category = row['CH_category'] if pd.notna(row['CH_category']) else 'Tidak Diketahui'
            popup = (
                f"<b>CH</b>: {row['CH']:.2f} mm<br>"
                f"<b>Kategori CH</b>: {category}<br>"
                f"<b>SH%</b>: {row['SH%']:.2f}<br>"
                f"<b>AnomCH</b>: {row['AnomCH']:.2f}"
            )
            folium.CircleMarker(
                location=[float(row['LAT']), float(row['LON'])],
                radius=5,
                color=ch_colors.get(category, '#000000'),
                fill=True,
                fill_opacity=0.8,
                popup=popup,
                stroke=False,
            ).add_to(cluster)
        cluster.add_to(map_obj)

    legend_html = '<div style="line-height:1.8;">'
    for label in ch_labels:
        legend_html += (
            f"<span style='display:inline-block;width:16px;height:16px;background:{ch_colors[label]};margin-right:8px;border-radius:3px;'></span>{label}<br>"
        )
    legend_html += '</div>'
    st.markdown('### Legenda Kategori CH', unsafe_allow_html=True)
    st.markdown(legend_html, unsafe_allow_html=True)

    st_folium(map_obj, width=1200, height=700)

    with st.expander('Tabel data hasil filter'):
        st.dataframe(
            selected[['LON', 'LAT', 'CH', 'CH_category', 'SH%', 'SHpercentil', 'AnomCH']].reset_index(drop=True).head(200),
            use_container_width=True,
        )
