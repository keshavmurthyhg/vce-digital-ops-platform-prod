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

# ---------------- SOURCE ----------------
st.sidebar.markdown("---")
source = st.sidebar.radio("Source", ["ALL", "AZURE", "SNOW", "PTC"])

if source != "ALL":
    base_df = df[df["Source"] == source]
else:
    base_df = df

# ---------------- FILTERS ----------------
st.sidebar.markdown("### 🔧 Filters")

def create_filter(data, col):
    vals = data[col].dropna().astype(str).unique().tolist()
    return st.sidebar.selectbox(col, ["ALL"] + sorted(vals)) if vals else "ALL"

state_filter = create_filter(base_df, "Status")
priority_filter = create_filter(base_df, "Priority")

release_filter = "ALL"
if source == "AZURE":
    release_filter = create_filter(base_df, "Release")

# ---------------- SEARCH FORM (FIXED CLEAR) ----------------
with st.form("search_form"):
    col1, col2 = st.columns([10,1])
    keyword = col1.text_input("🔍 Search")
    search_btn = col2.form_submit_button("Search")
    clear_btn = col2.form_submit_button("❌ Clear")

if clear_btn:
    keyword = ""

# ---------------- APPLY FILTER ----------------
filtered = base_df.copy()

if state_filter != "ALL":
    filtered = filtered[filtered["Status"] == state_filter]

if priority_filter != "ALL":
    filtered = filtered[filtered["Priority"] == priority_filter]

if release_filter != "ALL":
    filtered = filtered[filtered["Release"] == release_filter]

if keyword:
    filtered = filtered[
        filtered.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)
    ]

filtered = filtered.reset_index(drop=True)
filtered.index += 1

# ---------------- RESULTS ----------------
st.markdown(
    f"<h4 style='font-size:18px;'>🔢 Results: {len(filtered)}</h4>",
    unsafe_allow_html=True
)

# ---------------- ALIGNMENT ----------------
def style_df(df):
    return df.style.set_properties(**{'text-align': 'center'}).set_properties(
        subset=["Description","Created By","Assigned To"],
        **{'text-align': 'left'}
    )

cols = [
    "Number","Description","Priority","Status",
    "Created By","Created Date","Assigned To",
    "Resolution Date","Release","Source"
]

st.dataframe(style_df(filtered[cols]), use_container_width=True)

st.download_button(
    "⬇️ Download",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)

# ---------------- KPI (2 COLUMN GRID) ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")

def show_kpi(data):
    total = len(data)
    open_count = data["Status"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = data["Status"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled_count = data["Status"].astype(str).str.contains("cancel", case=False, na=False).sum()

    c1, c2 = st.sidebar.columns(2)
    c1.metric("Total", total)
    c2.metric("Open", open_count)

    c3, c4 = st.sidebar.columns(2)
    c3.metric("Closed", closed_count)
    c4.metric("Cancelled", cancelled_count)

show_kpi(base_df)
