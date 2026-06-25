import streamlit as st
import plotly.express as px
from utils import get_summary, load_data


def main() -> None:
    st.set_page_config(page_title="Dashboard Curah Hujan", page_icon="🌧️", layout="wide")
    st.title("Dashboard Visualisasi Curah Hujan")
    st.markdown(
        """
        Selamat datang di dashboard curah hujan. Data yang ditampilkan berasal dari file
        `BlendGSMAP_POS.202606dec02.xls` dengan titik-titik lokasi curah hujan di Indonesia.
        """
    )

    try:
        df = load_data()
    except Exception as exc:
        st.error(f"Data tidak dapat dimuat: {exc}")
        st.stop()

    if df.empty:
        st.warning("Data kosong setelah validasi. Tidak ada visualisasi yang dapat ditampilkan.")
        st.stop()

    summary = get_summary(df)

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Jumlah Lokasi", f"{summary['rows']:,}")
        col2.metric("Rata-rata CH", f"{summary['mean_ch']:.1f} mm")
        col3.metric("Rata-rata SH%", f"{summary['mean_sh']:.1f}")
        col4.metric("Rata-rata AnomCH", f"{summary['mean_anom']:.2f}")

    st.markdown("---")

    st.subheader("Ringkasan Statistik")
    col1, col2, col3 = st.columns(3)
    col1.metric("CH minimum", f"{summary['min_ch']:.2f}")
    col2.metric("CH maksimum", f"{summary['max_ch']:.2f}")
    col3.metric("Korelasi CH-AnomCH", f"{summary['corr_ch_anom']:.2f}")

    fig_ch = px.histogram(
        df,
        x="CH",
        nbins=40,
        title="Distribusi Curah Hujan (CH)",
        labels={"CH": "Curah Hujan (mm)"},
        template="plotly_white",
    )
    fig_sh = px.histogram(
        df,
        x="SHpercentil",
        nbins=40,
        title="Distribusi SHpercentil",
        labels={"SHpercentil": "SHpercentil"},
        template="plotly_white",
    )

    st.plotly_chart(fig_ch, use_container_width=True)
    st.plotly_chart(fig_sh, use_container_width=True)

    st.subheader("Preview Data")
    st.dataframe(df.head(15), use_container_width=True)

    st.markdown(
        """
        **Petunjuk navigasi:**
        - Gunakan halaman **1 Visual Curah Hujan** untuk melihat peta titik curah hujan.
        - Gunakan halaman **2 Visual Sifat Hujan** untuk analisis `SH%` dan `SHpercentil`.
        - Gunakan halaman **3 Grafik Curah Hujan** untuk tampilan CH dan anomali.
        - Gunakan halaman **4 Grafik Sifat Hujan** untuk korelasi dan distribusi sifat hujan.
        """
    )


if __name__ == "__main__":
    main()
