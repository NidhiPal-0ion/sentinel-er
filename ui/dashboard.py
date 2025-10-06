# ui/dashboard.py
import streamlit as st
import requests

st.title("Sentinel ER Dashboard")
entity_id = st.text_input("Enter Student/Staff ID")
if st.button("Get Timeline"):
    res = requests.get(f"http://127.0.0.1:8000/timeline/{entity_id}")
    st.write(res.json())
