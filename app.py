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
            "ID": df.get("id"),
            "Title": df.get("title"),
            "State": df.get("state"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved date"),
            "Release": df.get("release_windchill"),
            "Priority": None,
            "Source": "Azure"
        })

    def build_snow(df):
        return pd.DataFrame({
            "ID": df.get("number"),
            "Title": df.get("short description"),
            "State": df.get("incident state"),
            "Created Date": df.get("created"),
            "Assigned To": df.get("assigned to"),
            "Resolved Date": df.get("resolved"),
            "Release": None,
            "Priority": df.get("priority"),
            "Source": "SNOW"
        })

    def build_ptc(df):
        return pd.DataFrame({
            "ID": df.get("case number"),
            "Title": df.get("subject"),
            "State": df.get("status"),
            "Created Date": df.get("created date"),
            "Assigned To": df.get("case assignee"),
            "Resolved Date": df.get("resolved date"),
            "Release": None,
            "Priority": df.get("severity"),
            "Source": "PTC"
        })

    return pd.concat([build_azure(azure), build_snow(snow), build_ptc(ptc)], ignore_index=True)


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")

menu = st.sidebar.selectbox("Menu", ["Search Tool", "Dashboard (Coming)", "Reports (Coming)"])

st.sidebar.markdown("---")

# ---------------- KPI (ALWAYS VISIBLE) ----------------
st.sidebar.markdown("### 📊 KPI")

def calculate_kpi(data):
    total = len(data)
    open_count = data["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed = data["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled = data["State"].astype(str).str.contains("cancel", case=False, na=False).sum()
    return total, open_count, closed, cancelled

# ---------------- SEARCH ----------------
st.markdown("### 🔍 Search")

col1, col2 = st.columns([10,1])
keyword = col1.text_input("", placeholder="Type keyword and press Enter")

if col2.button("❌"):
    st.experimental_rerun()

# BEFORE SEARCH KPI
if not keyword:
    t,o,c,x = calculate_kpi(df)
    st.sidebar.metric("Total", t)
    st.sidebar.metric("Open", o)
    st.sidebar.metric("Closed", c)
    st.sidebar.metric("Cancelled", x)

    st.info("🔍 Enter a keyword to begin search")
    st.stop()

# ---------------- SEARCH FILTER ----------------
filtered = df[
    df.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)
]

# AFTER SEARCH KPI
t,o,c,x = calculate_kpi(filtered)
st.sidebar.metric("Total", t)
st.sidebar.metric("Open", o)
st.sidebar.metric("Closed", c)
st.sidebar.metric("Cancelled", x)

# ---------------- FILTERS ----------------
st.sidebar.markdown("### 🔧 Filters")

state = st.sidebar.selectbox("State", ["ALL"] + sorted(filtered["State"].dropna().unique()))

if state != "ALL":
    filtered = filtered[filtered["State"] == state]

# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

def show(data):

    data = data.reset_index(drop=True)
    data.index += 1

    st.markdown(f"#### Results: {len(data)}")

    cols = ["ID","Title","Release","State","Created Date","Assigned To","Resolved Date","Priority"]
    cols = [c for c in cols if c in data.columns]

    st.dataframe(data[cols], use_container_width=True, height=450)

    st.download_button("⬇️ Download", data.to_csv(index=False), "data.csv")


with tab_all:
    show(filtered)

with tab_az:
    show(filtered[filtered["Source"]=="Azure"])

with tab_snow:
    show(filtered[filtered["Source"]=="SNOW"])

with tab_ptc:
    show(filtered[filtered["Source"]=="PTC"])
