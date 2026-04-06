import streamlit as st

def style_df(df):
    return df.style.set_properties(**{'text-align': 'center'}).set_properties(
        subset=["Description","Created By","Assigned To"],
        **{'text-align': 'left'}
    )

def show_table(df):

    df.index += 1

    st.markdown(
        f"<h4 style='font-size:18px;'>🔢 Results: {len(df)}</h4>",
        unsafe_allow_html=True
    )

    cols = [
        "Number","Description","Priority","Status",
        "Created By","Created Date","Assigned To",
        "Resolution Date","Release","Source"
    ]

    st.dataframe(style_df(df[cols]), use_container_width=True)

    st.download_button(
        "⬇️ Download",
        df.to_csv(index=False),
        "filtered_data.csv"
    )
