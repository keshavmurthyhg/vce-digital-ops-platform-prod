import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Unified Dashboard (SNOW / Azure / PTC)")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    # 🔁 Replace with your OneDrive links later
    azure = pd.read_excel("https://volvogroup-my.sharepoint.com/:x:/r/personal/keshavamurthy_hg_consultant_volvo_com/Documents/Keshava/AMS-Windchill/Keshava/Windchill%20Support%20Documents/Azure%20Bugs/Bug%20Report/All%20VCE%20Bugs/All%20VCE%20Bugs_31Mar2026.csv?d=wf77ad2caf2d64196a8517f3c36b1b83e&csf=1&web=1&e=leg0qx")
    ptc = pd.read_excel("https://volvogroup-my.sharepoint.com/:x:/r/personal/keshavamurthy_hg_consultant_volvo_com/Documents/Keshava/AMS-Windchill/Keshava/Windchill%20Support%20Documents/PTC_Cases_Report/PTC%20Report/PTC%20Cases%20Report_30Mar2026.xlsx?d=w9b941604acc94594957f50bfc4bc55a7&csf=1&web=1&e=y259KV")
    snow = pd.read_excel("https://volvogroup-my.sharepoint.com/:x:/r/personal/keshavamurthy_hg_consultant_volvo_com/Documents/Keshava/AMS-Windchill/Keshava/Windchill%20Support%20Documents/VCE-Incidents_Report/Reports/incident_31Mar2026.xlsx?d=w4b1ad8a4e5314c98ae5ef5a767693646&csf=1&web=1&e=gz9MyI")

    azure["Source"] = "Azure"
    snow["Source"] = "SNOW"
    ptc["Source"] = "PTC"

    df = pd.concat([azure, snow, ptc], ignore_index=True)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔧 Filters")

def create_filter(column):
    if column in df.columns:
        values = ["ALL"] + sorted(df[column].dropna().astype(str).unique().tolist())
        return st.sidebar.selectbox(column, values)
    return "ALL"

state = create_filter("State")
assigned = create_filter("Assigned To")
release = create_filter("Release_windchill")

# ---------------- SEARCH ----------------
keyword = st.text_input("🔍 Search (All Columns)")

filtered = df.copy()

# Apply filters
if state != "ALL":
    filtered = filtered[filtered["State"].astype(str) == state]

if assigned != "ALL":
    filtered = filtered[filtered["Assigned To"].astype(str) == assigned]

if release != "ALL":
    filtered = filtered[filtered["Release_windchill"].astype(str) == release]

# Keyword search (Excel-like)
if keyword:
    filtered = filtered[
        filtered.apply(
            lambda row: row.astype(str).str.contains(keyword, case=False).any(),
            axis=1
        )
    ]

# ---------------- OUTPUT ----------------
st.write(f"### 🔢 Results: {len(filtered)}")

st.dataframe(filtered, use_container_width=True)

st.download_button(
    "⬇️ Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_data.csv"
)
