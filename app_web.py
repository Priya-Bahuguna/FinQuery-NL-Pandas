# app_web.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import List

st.set_page_config(page_title="FinQuery - NL Financial Analyzer", layout="wide")

# ---------- Helpers ----------
def load_and_transform(path: str) -> pd.DataFrame:
    """
    Load CSV and transform if metrics are rows and years are columns.
    Expected original format (like your file):
        Unnamed:0,2012-12-31,2013-12-31,...
        Total Assets, 88970, 84896,...
    After transform we want:
        Year | Total Assets | Revenue | ...
    """
    df = pd.read_csv(path, dtype=str)
    # If first column header is something like "Unnamed: 0" and years are columns,
    # we assume metrics are rows and years are columns -> transpose
    first_col = df.columns[0]
    # simple heuristic: if many column names look like dates (contain '-'), transpose
    date_like_count = sum(1 for c in df.columns if "-" in str(c))
    if date_like_count >= 2:
        # remove any totally empty columns
        df = df.dropna(axis=1, how="all")
        df = df.set_index(first_col).T.reset_index()
        df = df.rename(columns={"index": "Year"})
    else:
        # assume already in standard "Year | MetricA | MetricB" format
        if "Year" not in df.columns:
            # try to standardize small cases
            df = df.rename(columns={first_col: "Year"})
    # convert numeric columns
    for col in df.columns:
        if col == "Year":
            continue
        df[col] = pd.to_numeric(df[col].str.replace(",", "").str.replace("(", "-").str.replace(")", ""), errors="coerce")
    return df

def find_matching_columns(df: pd.DataFrame, keywords: List[str]) -> List[str]:
    cols = []
    for kw in keywords:
        for col in df.columns:
            if col == "Year":
                continue
            if kw.lower() in col.lower():
                if col not in cols:
                    cols.append(col)
    return cols

def simple_nl_to_keywords(text: str) -> List[str]:
    # Try TextBlob if available for better nouns, otherwise simple tokenization
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        nouns = [w for (w, pos) in blob.tags if pos.startswith("NN")]
        if nouns:
            return nouns
    except Exception:
        pass
    # fallback: split and keep words longer than 3 chars
    tokens = [t.strip().lower() for t in text.replace(",", " ").split() if len(t.strip()) > 3]
    return tokens

# ---------- UI ----------
st.title("📊 FinQuery — NL Financial Data Analyzer")
st.markdown("Ask simple English questions or use controls on the left. Supports transposed financial CSVs (metrics as rows).")

# Sidebar controls
with st.sidebar:
    st.header("Data & Controls")
    data_path = st.text_input("CSV path (relative)", value="data/apple_income_statements.csv")
    load_btn = st.button("Load CSV")
    st.markdown("---")
    st.markdown("**Quick tips**")
    st.write("- Put your CSV in `data/` folder.")
    st.write("- If your file has metrics in rows (like your sample), app will transpose automatically.")
    st.markdown("---")
    st.subheader("Plot options")
    chart_type = st.selectbox("Chart type", ["Line (default)", "Bar"])
    smooth = st.checkbox("Smooth (rolling mean)", value=False)
    window = st.slider("Rolling window (if smoothing)", min_value=2, max_value=5, value=3)

# Load data
if "df" not in st.session_state:
    st.session_state.df = None

if load_btn or st.session_state.df is None:
    try:
        df = load_and_transform(data_path)
        st.session_state.df = df
        st.success("✅ Data loaded.")
    except FileNotFoundError:
        st.error(f"CSV not found at `{data_path}`. Put file in project folder or correct the path.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()
else:
    df = st.session_state.df

# show columns & quick data preview
st.subheader("Available Columns")
cols_list = list(df.columns)
st.code(cols_list, language="text")

# layout: left panel NL + selection, right panel chart + table
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("Natural Language Query")
    user_q = st.text_input("Type here (e.g., 'show total assets' or 'compare cash and total liabilities')")

    st.write("—or—")
    st.subheader("Manual selection")
    metric = st.selectbox("Choose a metric to plot", options=[c for c in df.columns if c != "Year"])
    multi = st.multiselect("Compare multiple metrics", options=[c for c in df.columns if c != "Year"], default=[metric])

    st.markdown("---")
    st.subheader("Derived Ratios (Quick)")
    if st.button("Debt-to-Equity ratio"):
        if "Total Liabilities" in df.columns and "Total Equity" in df.columns:
            df["Debt_to_Equity"] = df["Total Liabilities"] / df["Total Equity"]
            multi = ["Debt_to_Equity"]
        else:
            st.warning("Columns named 'Total Liabilities' and 'Total Equity' required for this ratio.")
    if st.button("Current Ratio (Current Assets / Current Liabilities)"):
        if "Total Current Assets" in df.columns and "Total Current Liabilities" in df.columns:
            df["Current_Ratio"] = df["Total Current Assets"] / df["Total Current Liabilities"]
            multi = ["Current_Ratio"]
        else:
            st.warning("Need 'Total Current Assets' and 'Total Current Liabilities' columns.")

with right_col:
    st.subheader("Chart & Table")

    # Determine which columns to show (NL or manual)
    chosen_cols = []
    if user_q and user_q.strip():
        keywords = simple_nl_to_keywords(user_q)
        st.write("🧩 Detected keywords:", keywords)
        matches = find_matching_columns(df, keywords)
        if matches:
            chosen_cols = matches
            st.success(f"Matched columns: {matches}")
        else:
            st.warning("No exact matches found via keywords. Try simpler words (e.g., 'assets', 'cash', 'liabilities') or use manual selection.")
    else:
        chosen_cols = multi if multi else [metric]

    # final chosen
    if not chosen_cols:
        st.info("Select metrics on the left or type a query.")
    else:
        # prepare data for plotting
        plot_df = df[["Year"] + chosen_cols].copy()
        # try to convert Year to readable form (keep as string for x-axis)
        # apply smoothing if requested
        if smooth and len(chosen_cols) > 0:
            for c in chosen_cols:
                plot_df[c] = plot_df[c].rolling(window=window, min_periods=1).mean()

        # Plot with matplotlib
        fig, ax = plt.subplots(figsize=(9, 5))
        x = plot_df["Year"]
        for c in chosen_cols:
            if chart_type.startswith("Line"):
                ax.plot(x, plot_df[c], marker='o', label=c)
            else:
                ax.bar([f"{i}_{c}" for i in range(len(x))], plot_df[c], label=c)
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=45, ha="right")
        ax.set_xlabel("Year")
        ax.set_ylabel("Value")
        ax.set_title(" vs ".join(chosen_cols))
        ax.legend(loc='best', fontsize='small')
        st.pyplot(fig)

        # show data
        st.markdown("### Data Table")
        st.dataframe(plot_df.style.format(precision=2, na_rep="-"))

# footer / help
st.markdown("---")
st.markdown("**Tips:** Try queries like `show total assets`, `compare cash and total liabilities`, `current ratio`.")
st.markdown("If Natural Language matching misses, use manual selection on the left.")

