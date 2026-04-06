import pandas as pd

def norm(df):
    df.columns = df.columns.str.strip().str.lower()
    return df

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

def load_data():
    azure = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/All-VCE-Bugs.csv")
    snow = pd.read_excel("https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/Snow-incident.xlsx", engine="openpyxl")
    ptc = pd.read_csv("https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/PTC-Cases-Report.csv")

    azure, snow, ptc = norm(azure), norm(snow), norm(ptc)

    return pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)
