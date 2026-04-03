import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- TITLE ----------------
st.title("⚙️ Ops Insight Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv")

    # ---------------- STANDARDIZE COLUMNS ----------------

    # Azure
    azure = azure.rename(columns={
        "ID": "ID",
        "Title": "Title",
        "State": "State",
        "Assigned To": "Assigned To",
        "Created Date": "Created Date",
        "Release_windchill": "Release"
    })

    # SNOW
    snow = snow.rename(columns={
        "Number": "ID",
        "Short description": "Title",
        "State": "State",
        "Assigned to": "Assigned To",
        "Opened": "Created Date",
        "Priority": "Priority",
        "Assignment group": "Assignment Group"
    })

    # PTC
    ptc = ptc.rename(columns={
        "Number": "ID",
        "Name": "Title",
        "State": "State",
        "Owner": "Assigned To",
        "Created On": "Created Date",
        "Plant": "Plant"
    })

    # Add Source column
    azure["Source"] = "Azure"
    snow["Source"] = "SNOW"
    ptc["Source"] = "PTC"

    # Combine all
    df = pd.concat([azure, snow, ptc], ignore_index=True)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔧 Filters")

source = st.sidebar.selectbox("Source", ["ALL", "Azure", "SNOW", "PTC"])

filtered = df.copy()

if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

# ---------------- FILTER FUNCTION ----------------
def create_filter(data, column):
    if column in data.columns:
        values = ["ALL"] + sorted(data[column].dropna().astype(str).unique().tolist())
        return st.sidebar.selectbox(column, values)
    return "ALL"

# ---------------- COMMON FILTER ----------------
state = create_filter(filtered, "State")

if state != "ALL":
    filtered = filtered[filtered["State"].astype(str) == state]

# ---------------- SOURCE-SPECIFIC FILTERS ----------------
if source == "Azure":
    assigned = create_filter(filtered, "Assigned To")
    release = create_filter(filtered, "Release")

    if assigned != "ALL":
        filtered = filtered[filtered["Assigned To"].astype(str) == assigned]

    if release != "ALL":
        filtered = filtered[filtered["Release"].astype(str) == release]

elif source == "SNOW":
    priority = create_filter(filtered, "Priority")
    group = create_filter(filtered, "Assignment Group")

    if priority != "ALL":
        filtered = filtered[filtered["Priority"].astype(str) == priority]

    if group != "ALL":
        filtered = filtered[filtered["Assignment Group"].astype(str) == group]

elif source == "PTC":
    owner = create_filter(filtered, "Assigned To")
    plant = create_filter(filtered, "Plant")

    if owner != "ALL":
        filtered = filtered[filtered["Assigned To"].astype(str) == owner]

    if plant != "ALL":
        filtered = filtered[filtered["Plant"].astype(str) == plant]

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search (All Columns)")

if keyword:
    filtered = filtered[
        filtered.apply(
            lambda row: row.astype(str).str.contains(keyword, case=False).any(),
            axis=1
        )
    ]

# ---------------- KPI SECTION ----------------
st.markdown("### 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total = len(filtered)

open_count = filtered[
    filtered["State"].astype(str).str.contains("Open|New", case=False, na=False)
].shape[0]

closed_count = filtered[
    filtered["State"].astype(str).str.contains("Closed|Resolved", case=False, na=False)
].shape[0]

azure_count = filtered[filtered["Source"] == "Azure"].shape[0]
snow_count = filtered[filtered["Source"] == "SNOW"].shape[0]
ptc_count = filtered[filtered["Source"] == "PTC"].shape[0]

col1.metric("Total Records", total)
col2.metric("Open / Active", open_count)
col3.metric("Closed / Resolved", closed_count)
col4.metric("Azure Records", azure_count)

col5, col6 = st.columns(2)
col5.metric("SNOW Records", snow_count)
col6.metric("PTC Records", ptc_count)

# ---------------- COLUMN ORDER FIX ----------------
desired_columns = [
    "Source",
    "ID",
    "Title",
    "State",
    "Assigned To",
    "Priority",
    "Assignment Group",
    "Release",
    "Plant",
    "Created Date"
]

final_cols = [col for col in desired_columns if col in filtered.columns]
filtered = filtered[final_cols]

# ---------------- RESULTS ----------------
st.write(f"### 🔢 Results: {len(filtered)}")

st.dataframe(filtered, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)
