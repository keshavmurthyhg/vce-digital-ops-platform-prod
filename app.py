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

    df = pd.concat([
        build_azure(azure).assign(Source="Azure"),
        build_snow(snow).assign(Source="SNOW"),
        build_ptc(ptc).assign(Source="PTC")
    ], ignore_index=True)

    return df


df = load_data()

# ---------------- HEADER ----------------
st.markdown("## ⚙️ Ops Insight Dashboard")

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search", placeholder="Type keyword and press Enter")

# ---------------- TABS ----------------
tab_all, tab_az, tab_snow, tab_ptc = st.tabs(["All", "Azure", "SNOW", "PTC"])

def process_tab(data):

    # Filters (LEFT SIDEBAR ONLY)
    st.sidebar.markdown("### 🔧 Filters")

    state = st.sidebar.selectbox("State", ["ALL"] + sorted(data["State"].dropna().unique().tolist()))

    if state != "ALL":
        data = data[data["State"] == state]

    if "Priority" in data.columns:
        vals = data["Priority"].dropna().unique()
        if len(vals) > 0:
            p = st.sidebar.selectbox("Priority", ["ALL"] + sorted(vals))
            if p != "ALL":
                data = data[data["Priority"] == p]

    # Search behavior (Google-like)
    if not keyword:
        st.info("🔍 Enter a keyword to begin search")
        return

    data = data[
        data.apply(lambda r: r.astype(str).str.contains(keyword, case=False).any(), axis=1)
    ]

    data = data.reset_index(drop=True)
    data.index += 1

    # KPI TOP
    col1, col2, col3, col4 = st.columns(4)

    total = len(data)
    open_count = data["State"].astype(str).str.contains("open|new", case=False, na=False).sum()
    closed_count = data["State"].astype(str).str.contains("closed|resolved", case=False, na=False).sum()
    cancelled = data["State"].astype(str).str.contains("cancel", case=False, na=False).sum()

    col1.metric("Total", total)
    col2.metric("Open", open_count)
    col3.metric("Closed", closed_count)
    col4.metric("Cancelled", cancelled)

    # Smaller result title
    st.markdown(f"#### Results: {len(data)}")

    cols = ["ID","Title","Release","State","Created By","Created Date","Assigned To","Resolved Date","Priority"]
    cols = [c for c in cols if c in data.columns]

    # CENTER ALIGN TABLE
    st.dataframe(
        data[cols].style.set_properties(**{'text-align': 'center'}),
        use_container_width=True
    )

    # Single download button
    st.download_button("⬇️ Download", data.to_csv(index=False), "data.csv")


with tab_all:
    process_tab(df)

with tab_az:
    process_tab(df[df["Source"]=="Azure"])

with tab_snow:
    process_tab(df[df["Source"]=="SNOW"])

with tab_ptc:
    process_tab(df[df["Source"]=="PTC"])
