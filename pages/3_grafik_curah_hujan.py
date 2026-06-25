import streamlit as st
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Grafik Curah Hujan", page_icon="📈", layout="wide")

st.title("Grafik Curah Hujan")
st.write("Grafik distribusi dan hubungan nilai curah hujan serta anomali pada dataset.")

try:
    df = load_data()
except Exception as exc:
    st.error(f"Data tidak dapat dimuat: {exc}")
    st.stop()

if df.empty:
    st.warning('Data kosong setelah validasi. Tidak ada visualisasi yang dapat ditampilkan.')
    st.stop()

if 'CH' not in df.columns:
    st.error('Kolom CH tidak ditemukan dalam data.')
    st.stop()

ch_min, ch_max = float(df['CH'].min()), float(df['CH'].max())
selected = st.sidebar.slider('Rentang CH', ch_min, ch_max, (ch_min, min(ch_max, ch_min + 120.0)), step=1.0)
filtered = df.query('CH >= @selected[0] and CH <= @selected[1]').copy()

st.write(f"Menampilkan **{len(filtered):,}** titik dengan CH di antara {selected[0]:.1f} dan {selected[1]:.1f}.")

if filtered.empty:
    st.warning('Tidak ada data yang cocok dengan rentang CH saat ini.')
else:
    fig_hist = px.histogram(
        filtered,
        x='CH',
        nbins=40,
        title='Histogram Curah Hujan (CH)',
        labels={'CH': 'Curah Hujan (mm)'},
        template='plotly_white',
    )
    fig_box = px.box(
        filtered,
        y='CH',
        title='Boxplot Curah Hujan (CH)',
        labels={'CH': 'Curah Hujan (mm)'},
        points='all',
        template='plotly_white',
    )
    fig_scatter = px.scatter(
        filtered.sample(n=min(len(filtered), 2000), random_state=2),
        x='CH',
        y='AnomCH',
        color='SH%',
        title='CH vs AnomCH',
        labels={'CH': 'Curah Hujan (mm)', 'AnomCH': 'AnomCH', 'SH%': 'SH%'},
        template='plotly_white',
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_hist, use_container_width=True)
    col2.plotly_chart(fig_box, use_container_width=True)
    st.plotly_chart(fig_scatter, use_container_width=True)
