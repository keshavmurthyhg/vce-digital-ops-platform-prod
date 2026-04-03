import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx", engine="openpyxl")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv")

    # Normalize
    def norm(df):
        df.columns = df.columns.str.strip().str.lower()
        return df

    azure, snow, ptc = norm(azure), norm(snow), norm(ptc)

    # ---------------- UNIFIED STRUCTURE ----------------

    def build_azure(df):
        return pd.DataFrame({
            "ID": df.get("id"),
            "Title": df.get("title"),
            "State": df.get("state"),
            "Created By": df.get("created by"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved date"),
            "Release": df.get("release_windchill"),
            "Priority": None
        })

    def build_snow(df):
        return pd.DataFrame({
            "ID": df.get("number"),
            "Title": df.get("short description"),
            "State": df.get("incident state"),
            "Created By": None,
            "Created Date": df.get("created"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved"),
            "Release": None,
            "Priority": df.get("priority")
        })

    def build_ptc(df):
        return pd.DataFrame({
            "ID": df.get("case number"),
            "Title": df.get("subject"),
            "State": df.get("status"),
            "Created By": df.get("case contact"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("case assignee"),
            "Resolved Date": df.get("resolved date"),
            "Release": None,
            "Priority": df.get("severity")
        })

    azure = build_azure(azure)
    snow = build_snow(snow)
    ptc = build_ptc(ptc)

    azure["Source"] = "Azure"
    snow["Source"] = "SNOW"
    ptc["Source"] = "PTC"

    df = pd.concat([azure, snow, ptc], ignore_index=True)

    return df


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

# MENU PLACEHOLDER
menu = st.sidebar.selectbox("Menu", ["Search Tool"])

st.sidebar.markdown("### 🔧 Filters")

source = st.sidebar.selectbox("Source", ["ALL", "Azure", "SNOW", "PTC"])

filtered = df.copy()

if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

# ---------------- FILTER FUNCTION ----------------
def create_filter(data, column):
    vals = data[column].dropna().astype(str).unique().tolist()
    if len(vals) == 0:
        return "ALL"
    return st.sidebar.selectbox(column, ["ALL"] + sorted(vals))

# ---------------- FILTERS ----------------
state = create_filter(filtered, "State")

if state != "ALL":
    filtered = filtered[filtered["State"] == state]

# Remove Assigned To default (as per your note)

if source == "Azure":
    release = create_filter(filtered, "Release")
    if release != "ALL":
        filtered = filtered[filtered["Release"] == release]

elif source == "SNOW":
    priority = create_filter(filtered, "Priority")
    if priority != "ALL":
        filtered = filtered[filtered["Priority"] == priority]

elif source == "PTC":
    priority = create_filter(filtered, "Priority")
    if priority != "ALL":
        filtered = filtered[filtered["Priority"] == priority]

# ---------------- KPI ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")

total = len(filtered)
open_count = filtered["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
closed_count = filtered["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
cancelled_count = filtered["State"].astype(str).str.contains("cancel", case=False, na=False).sum()

col1, col2 = st.sidebar.columns(2)
col1.metric("Total", total)
col2.metric("Open", open_count)

col3, col4 = st.sidebar.columns(2)
col3.metric("Closed", closed_count)
col4.metric("Cancelled", cancelled_count)

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search")

if keyword:
    filtered = filtered[
        filtered.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
    ]

# ---------------- SERIAL NUMBER RESET ----------------
filtered = filtered.reset_index(drop=True)
filtered.index = filtered.index + 1

# ---------------- TABLE ----------------
st.write(f"### 🔢 Results: {len(filtered)}")

cols = [
    "Source",
    "ID",
    "Title",
    "Release",
    "State",
    "Created By",
    "Created Date",
    "Assigned To",
    "Resolved Date",
    "Priority"
]

cols = [c for c in cols if c in filtered.columns]

st.dataframe(filtered[cols], use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)
