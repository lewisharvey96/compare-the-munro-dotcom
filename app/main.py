import os

import googlemaps
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation

from compare_the_munro_dotcom.utils import ROOT_FLD, get_commute_time_hours

load_dotenv()

st.set_page_config(page_title="Compare the munro .com", page_icon=":mountain:", layout="wide")

st.markdown(
    """
<style>
	[data-testid="stDecoration"] {
		display: none;
	}

</style>""",
    unsafe_allow_html=True,
)

hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
</style>

"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

TABLE_COLUMNS = [
    "route_name",
    "distance",
    "time_median",
    "ascent",
    "munros_climbed",
    "rating",
    "grade",
    "bog_factor",
    "calories_per_kg",
    "number_of_munros",
    "route_page_link",
]
MAP_CENTER = {"lat": 57.3, "lon": -4.28}

st.title(":mountain: Compare the munro .com")

location = streamlit_geolocation()
current_location = (location["latitude"], location["longitude"])

routes_df = pd.read_csv(ROOT_FLD / "data" / "all_routes_add_features.csv").set_index("name")

gmaps = googlemaps.Client(key=os.environ.get("GMAPS_API_KEY"))

st.markdown("Click to use your location and calculate commute time (driving) if possible.")
st.markdown(
    "The map shows the start of each route with the **size** of the marker proportional to the **distance** of "
    "the route "
    "and the **color** is proportional to the **ascent** gained."
)

fig = px.scatter_mapbox(
    routes_df,
    lat="start_lat",
    lon="start_lon",
    color="ascent",
    size="distance",
    hover_name="route_name",
    hover_data=list(set(TABLE_COLUMNS) - set(["route_page_link"])),
    custom_data=["route_page_link"],
    mapbox_style="open-street-map",
    center=MAP_CENTER,
    zoom=6.5,
    height=800,
    color_continuous_scale=px.colors.sequential.Reds,
)

with st.expander("Map of Routes", expanded=True):
    st.plotly_chart(fig)

st_df = st.empty()
st_df.dataframe(
    routes_df[TABLE_COLUMNS], column_config={"route_page_link": st.column_config.LinkColumn("route_page_link")}
)

if location["latitude"] is not None:
    routes_df["commute_time"] = get_commute_time_hours(
        gmaps, current_location, routes_df[["start_lat", "start_lon"]].to_records(index=False)
    )
    routes_df["total_time"] = routes_df["time_median"] + routes_df["commute_time"]
    TABLE_COLUMNS.insert(2, "commute_time")
    TABLE_COLUMNS.insert(3, "total_time")
    st_df.dataframe(
        routes_df[TABLE_COLUMNS], column_config={"route_page_link": st.column_config.LinkColumn("route_page_link")}
    )
