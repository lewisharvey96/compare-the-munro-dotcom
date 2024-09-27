from pathlib import Path

import googlemaps
import pandas as pd
import streamlit as st
from calcs import get_commute_time_hours
from plots import TABLE_COLUMNS, _create_map_fig
from streamlit_geolocation import streamlit_geolocation

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

st.title(":mountain: Compare the munro .com")

ROOT_FLD = Path(__file__).parent

location = streamlit_geolocation()
current_location = (location["latitude"], location["longitude"], "Current Location")

if location["latitude"] is not None:
    st.session_state["current_location"] = current_location

routes_df = pd.read_csv(ROOT_FLD / "data" / "all_routes_add_features.csv").set_index("name")

gmaps = googlemaps.Client(key=st.secrets["GMAPS_API_KEY"])

st.markdown("Click to use your location and calculate commute time (driving) if possible.")
st.markdown(
    "The map shows the start of each route with the **size** of the marker proportional to the **distance** of "
    "the route "
    "and the **color** is proportional to the **ascent** gained."
)

with st.expander("Map of Routes", expanded=True):
    st_fig = st.empty()
    if st.session_state.get("current_location", None):
        fig = _create_map_fig(routes_df, [current_location])
    else:
        fig = _create_map_fig(routes_df)
    st_fig.plotly_chart(fig)

st_df = st.empty()

highlight_points = []

if st.session_state.get("current_location", None):
    with st.spinner("Calculating commute times..."):
        routes_df["commute_time"] = get_commute_time_hours(
            gmaps, current_location, routes_df[["start_lat", "start_lon"]].to_records(index=False)
        )
        routes_df["total_time"] = routes_df["time_median"] + routes_df["commute_time"]
        highlight_points.append(current_location)

selection_event = st_df.dataframe(
    routes_df.filter(items=TABLE_COLUMNS),
    column_config={"route_page_link": st.column_config.LinkColumn("route_page_link")},
    on_select="rerun",
    selection_mode="multi-row",
)

selected_rows = selection_event.selection.rows  # type: ignore
if selected_rows:
    highlight_points.extend(
        [
            (i["start_lat"], i["start_lon"], i["route_name"])
            for i in routes_df.iloc[selected_rows].to_dict(orient="records")
        ]
    )

if set(highlight_points) - {current_location}:
    st_fig.plotly_chart(_create_map_fig(routes_df, highlight_points))
