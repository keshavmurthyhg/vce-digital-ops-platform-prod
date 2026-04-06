import streamlit as st

def clear_search():
    st.session_state.search_text = ""

def search_box():
    if "search_text" not in st.session_state:
        st.session_state.search_text = ""

    col1, col2 = st.columns([10,1])

    with col1:
        keyword = st.text_input("🔍 Search", key="search_text")

    with col2:
        st.button("❌", on_click=clear_search)

    return keyword
