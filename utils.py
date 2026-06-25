import pandas as pd
import streamlit as st
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "BlendGSMAP_POS.202606dec02.xls"
REQUIRED_COLUMNS = ["LON", "LAT", "CH", "SH%", "SHpercentil", "AnomCH"]

@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE, engine="xlrd")
    df = df.rename(columns=lambda name: name.strip() if isinstance(name, str) else name)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Data file is missing required columns: {missing_columns}")

    df = df[REQUIRED_COLUMNS].copy()
    df = df.astype({col: float for col in REQUIRED_COLUMNS})
    return df

@st.cache_data
def get_summary(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "min_ch": float(df["CH"].min()),
        "max_ch": float(df["CH"].max()),
        "mean_ch": float(df["CH"].mean()),
        "median_ch": float(df["CH"].median()),
        "min_sh": float(df["SH%"].min()),
        "max_sh": float(df["SH%"].max()),
        "mean_sh": float(df["SH%"].mean()),
        "median_sh": float(df["SH%"].median()),
        "mean_anom": float(df["AnomCH"].mean()),
        "corr_ch_anom": float(df[["CH", "AnomCH"]].corr().iloc[0, 1]),
    }
