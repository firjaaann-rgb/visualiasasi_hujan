import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Grafik Sifat Hujan", page_icon="📉", layout="wide")

st.title("Grafik Sifat Hujan")
st.write("Grafik visualisasi hubungan sifat hujan dengan curah hujan dan anomali.")

df = load_data()
filtered = df.copy()

filtered['AnomCategory'] = pd.cut(
    filtered['AnomCH'],
    bins=[-999, -5, 5, 20, 999],
    labels=['Negatif', 'Dekat Nol', 'Positif', 'Ekstrem'],
)

fig_violin_sh = px.violin(
    filtered,
    y='SH%',
    box=True,
    points='all',
    title='Violin Plot SH%'
)
fig_violin_shp = px.violin(
    filtered,
    y='SHpercentil',
    box=True,
    points='all',
    title='Violin Plot SHpercentil'
)
fig_corr = px.imshow(
    filtered[['CH', 'SH%', 'SHpercentil', 'AnomCH']].corr(),
    text_auto=True,
    title='Matriks Korelasi',
    color_continuous_scale='RdBu_r',
    labels=dict(x='Variabel', y='Variabel', color='Korelasi'),
)
fig_scatter = px.scatter(
    filtered.sample(n=min(len(filtered), 2000), random_state=3),
    x='SHpercentil',
    y='CH',
    color='AnomCategory',
    title='SHpercentil vs Curah Hujan (CH)',
    labels={'SHpercentil': 'SHpercentil', 'CH': 'Curah Hujan (mm)'},
)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_violin_sh, use_container_width=True)
col2.plotly_chart(fig_violin_shp, use_container_width=True)
st.plotly_chart(fig_corr, use_container_width=True)
st.plotly_chart(fig_scatter, use_container_width=True)
