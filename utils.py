import pandas as pd
import streamlit as st
from pathlib import Path
from typing import List

DATA_FILE = Path(__file__).parent / "data" / "BlendGSMAP_POS.202606dec02.xls"
REQUIRED_COLUMNS = ["LON", "LAT", "CH", "SH%", "SHpercentil", "AnomCH"]
NUMERIC_COLUMNS = REQUIRED_COLUMNS.copy()


def _warn(message: str) -> None:
    st.warning(message)


def _is_valid_dataframe(df: pd.DataFrame) -> bool:
    return df is not None and not df.empty


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE, engine="xlrd")
    df.rename(columns=lambda name: name.strip() if isinstance(name, str) else name, inplace=True)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Data file is missing required columns: {missing_columns}")

    df = df[REQUIRED_COLUMNS].copy()

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    invalid_counts = df[NUMERIC_COLUMNS].isna().sum()
    if invalid_counts.any():
        invalid_columns = [f"{col} ({invalid_counts[col]})" for col in invalid_counts.index if invalid_counts[col] > 0]
        _warn(
            "Beberapa nilai tidak valid atau hilang dan telah diabaikan pada kolom: "
            + ", ".join(invalid_columns)
        )

    df = df.dropna(subset=NUMERIC_COLUMNS).reset_index(drop=True)
    if df.empty:
        raise ValueError(
            "Data tidak memiliki baris valid setelah konversi numerik. Periksa file sumber dan kolom yang dibutuhkan."
        )

    return df


@st.cache_data
def get_summary(df: pd.DataFrame) -> dict:
    if not _is_valid_dataframe(df):
        return {}

    corr_value = df[["CH", "AnomCH"]].corr().iloc[0, 1]
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
        "corr_ch_anom": float(corr_value) if pd.notna(corr_value) else 0.0,
    }


def safe_cut(series: pd.Series, bins: List[float], labels: List[str], right: bool = True) -> pd.Series:
    result = pd.cut(series, bins=bins, labels=labels, right=right)
    return result.astype(pd.CategoricalDtype(categories=labels, ordered=True))


def category_counts(df: pd.DataFrame, category_column: str, labels: List[str], value_name: str = "Jumlah") -> pd.DataFrame:
    counts = df[category_column].value_counts(dropna=False).reindex(labels, fill_value=0)
    return counts.rename_axis(category_column).reset_index(name=value_name)


def group_stats(df: pd.DataFrame, group_columns: List[str], agg_dict: dict) -> pd.DataFrame:
    return df.groupby(group_columns, observed=False).agg(agg_dict)
