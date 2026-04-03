import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():

    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/Snow-incident.xlsx", engine="openpyxl")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/snow-ptc-azure-dashboard/main/PTC-Cases-Report.csv")

    def norm(df):
        df.columns = df.columns.str.strip().str.lower()
        return df

    azure, snow, ptc = norm(azure), norm(snow), norm(ptc)

    def build_azure(df):
        return pd.DataFrame({
            "Number": df.get("id"),
            "Description": df.get("title"),
            "Status": df.get("state"),
            "Created By": df.get("created by"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("assigned to"),
            "Resolution Date": df.get("resolved date"),
            "Release": df.get("release_windchill"),
            "Priority": None,
            "Source": "AZURE"
        })

    def build_snow(df):
        return pd.DataFrame({
            "Number": df.get("number"),
            "Description": df.get("short description"),
            "Status": df.get("incident state"),
            "Created By": df.get("opened by"),
            "Created Date": df.get("created"),
            "Assigned To": df.get("assigned to"),
            "Resolution Date": df.get("resolved"),
            "Release": None,
            "Priority": df.get("priority"),
            "Source": "SNOW"
        })

    def build_ptc(df):
        return pd.DataFrame({
            "Number": df.get("case number"),
            "Description": df.get("subject"),
            "Status": df.get("status"),
            "Created By": df.get("case contact"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("case assignee"),
            "Resolution Date": df.get("resolved date"),
            "Release": None,
            "Priority": df.get("severity"),
            "Source": "PTC"
        })

    return pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Menu", ["Search Tool"])

# ---------------- KPI ----------------
def show_kpi(data):
    total = len(data)
    open_count = data["Status"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = data["Status"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled_count = data["Status"].astype(str).str.contains("cancel", case=False, na=False).sum()

    col1, col2 = st.sidebar.columns(2)
    col1.metric("Total", total)
    col2.metric("Open", open_count)

    col3, col4 = st.sidebar.columns(2)
    col3.metric("Closed", closed_count)
    col4.metric("Cancelled", cancelled_count)

st.sidebar.markdown("### 📊 KPI")
show_kpi(df)

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search")

# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

# ---------------- FILTERS (ONLY ONCE, BASED ON ACTIVE TAB) ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Filters")

active_source = st.session_state.get("active_tab", "ALL")

# Helper for filter
def create_filter(data, col):
    vals = data[col].dropna().astype(str).unique().tolist()
    return st.sidebar.selectbox(col, ["ALL"] + sorted(vals)) if vals else "ALL"

# Base dataset for filters
if active_source == "AZURE":
    base_df = df[df["Source"] == "AZURE"]
elif active_source == "SNOW":
    base_df = df[df["Source"] == "SNOW"]
elif active_source == "PTC":
    base_df = df[df["Source"] == "PTC"]
else:
    base_df = df

# Filters
state_filter = create_filter(base_df, "Status")
priority_filter = create_filter(base_df, "Priority")

release_filter = "ALL"
if active_source == "AZURE":
    release_filter = create_filter(base_df, "Release")

# ---------------- APPLY FILTER ----------------
def apply_filters(data):

    if state_filter != "ALL":
        data = data[data["Status"] == state_filter]

    if priority_filter != "ALL":
        data = data[data["Priority"] == priority_filter]

    if release_filter != "ALL":
        data = data[data["Release"] == release_filter]

    if keyword:
        data = data[data.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)]

    return data.reset_index(drop=True)

# ---------------- TABLE ----------------
def show_table(data, source):
    st.session_state["active_tab"] = source

    data = apply_filters(data)
    data.index += 1

    st.write(f"### 🔢 Results: {len(data)}")

    cols = [
        "Number","Description","Priority","Status",
        "Created By","Created Date","Assigned To",
        "Resolution Date","Release","Source"
    ]

    st.dataframe(data[cols], use_container_width=True)

    st.download_button(
        "⬇️ Download",
        data.to_csv(index=False),
        "filtered_data.csv",
        key=f"download_{source}"
    )

# ---------------- TAB CONTENT ----------------
with tab_all:
    show_table(df, "ALL")

with tab_az:
    show_table(df[df["Source"] == "AZURE"], "AZURE")

with tab_snow:
    show_table(df[df["Source"] == "SNOW"], "SNOW")

with tab_ptc:
    show_table(df[df["Source"] == "PTC"], "PTC")
