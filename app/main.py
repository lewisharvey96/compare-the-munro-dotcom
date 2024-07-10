import streamlit as st
from streamlit_geolocation import streamlit_geolocation

location = streamlit_geolocation()

st.write(location)