import streamlit as st
from modules.data_loader import load_data
from modules.filters import create_filter, apply_filters
from modules.kpi import show_kpi
from modules.search import search_box
from modules.table import show_table

st.set_page_config(layout="wide")

# ---------------- LOAD ----------------
df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

st.sidebar.selectbox("Menu", ["Search Tool"])

# ---------------- SOURCE ----------------
st.sidebar.markdown("### Source")
source = st.sidebar.radio("", ["ALL","AZURE","SNOW","PTC"], horizontal=True)

base_df = df if source == "ALL" else df[df["Source"] == source]

# ---------------- FILTERS ----------------
st.sidebar.markdown("### 🔧 Filters")

state = create_filter(base_df, "Status")
priority = create_filter(base_df, "Priority")
release = create_filter(base_df, "Release") if source == "AZURE" else "ALL"

# ---------------- SEARCH ----------------
keyword = search_box()

# ---------------- FILTER APPLY ----------------
filtered = apply_filters(base_df, state, priority, release, keyword)

# ---------------- TABLE ----------------
show_table(filtered)

# ---------------- KPI ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")
show_kpi(base_df)
