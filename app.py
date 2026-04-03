import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- TITLE ----------------
st.markdown("## ⚙️ Ops Insight Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    # Azure (CSV)
    azure = pd.read_csv(
        "https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv"
    )

    # SNOW (Excel)
    snow = pd.read_excel(
        "https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx",
        engine="openpyxl"
    )

    # PTC (CSV)
    ptc = pd.read_csv(
        "https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv"
    )

    # ---------------- NORMALIZE COLUMN NAMES ----------------
    azure.columns = azure.columns.str.strip().str.lower()
    snow.columns = snow.columns.str.strip().str.lower()
    ptc.columns = ptc.columns.str.strip().str.lower()

    # ---------------- SAFE MAPPING FUNCTION ----------------
    def map_columns(df, mapping):
        new_df = pd.DataFrame()
        for new_col, possible_cols in mapping.items():
            for col in possible_cols:
                if col in df.columns:
                    new_df[new_col] = df[col]
                    break
            else:
                new_df[new_col] = None
        return new_df

    # ---------------- COLUMN MAPPINGS ----------------

    azure_map = {
        "ID": ["id"],
        "Title": ["title"],
        "State": ["state"],
        "Assigned To": ["assigned to"],
        "Created Date": ["created date"],
        "Release": ["release_windchill"]
    }

    snow_map = {
        "ID": ["number"],
        "Title": ["short description"],
        "State": ["state"],
        "Assigned To": ["assigned to"],
        "Created Date": ["opened"],
        "Priority": ["priority"],
        "Assignment Group": ["assignment group"]
    }

    ptc_map = {
        "ID": ["number"],
        "Title": ["name"],
        "State": ["state"],
        "Assigned To": ["owner"],
        "Created Date": ["created on"],
        "Plant": ["plant"]
    }

    # ---------------- APPLY MAPPING ----------------
    azure_clean = map_columns(azure, azure_map)
    snow_clean = map_columns(snow, snow_map)
    ptc_clean = map_columns(ptc, ptc_map)

    # ---------------- ADD SOURCE ----------------
    azure_clean["Source"] = "Azure"
    snow_clean["Source"] = "SNOW"
    ptc_clean["Source"] = "PTC"

    # ---------------- COMBINE ----------------
    df = pd.concat([azure_clean, snow_clean, ptc_clean], ignore_index=True)

    return df


df = load_data()

# ---------------- SIDEBAR ----------------
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

# ---------------- SOURCE FILTERS ----------------
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
keyword = st.text_input("🔍 Search")

if keyword:
    filtered = filtered[
        filtered.apply(
            lambda row: row.astype(str).str.contains(keyword, case=False).any(),
            axis=1
        )
    ]

# ---------------- LAYOUT ----------------
left, right = st.columns([1, 3])

# KPI LEFT
with left:
    st.markdown("### 📊 KPIs")

    total = len(filtered)
    open_count = filtered["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = filtered["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()

    st.metric("Total", total)
    st.metric("Open", open_count)
    st.metric("Closed", closed_count)
    st.metric("Azure", (filtered["Source"] == "Azure").sum())
    st.metric("SNOW", (filtered["Source"] == "SNOW").sum())
    st.metric("PTC", (filtered["Source"] == "PTC").sum())

# TABLE RIGHT
with right:

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

    st.write(f"### 🔢 Results: {len(filtered)}")
    st.dataframe(filtered, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)
