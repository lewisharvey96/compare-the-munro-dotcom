import pandas as pd

data = pd.read_csv("all_route_pages_data.csv")

data.head()

# +
import os

import googlemaps
import pandas as pd
import plotly.express as px
import matplotlib
import matplotlib.cm as cm

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation
# -

TABLE_COLUMNS = ["route_name", "distance", "ascent", "munros_climbed", "rating", "grade", "bog_factor", "route_page_link"]
data[TABLE_COLUMNS]

str(dict_to_html({"{"+i+"}":"{"+i+"}" for i in data.to_dict(orient="records")[0].keys()})).replace(" ", "")

"<i>"

# +
import plotly.express as px
import plotly.graph_objects as go

MAP_CENTER = {'lat': 57.3, 'lon': -4.28}

norm = matplotlib.colors.Normalize(vmin=min(data["ascent"]), vmax=max(data["ascent"]), clip=True)
mapper = cm.ScalarMappable(norm=norm, cmap=cm.Reds)
node_color = [(r, g, b) for r, g, b, a in mapper.to_rgba(data["ascent"])]

def dict_to_html(d):
    text = ''
    text += '<p>'.join(['<b>{0}</b>: {1}'.format(k, v) for k, v in d.items()])
    return text

fig = go.Figure((
    go.Scattermapbox(
        lat=data["start_lat"],
        lon=data["start_lon"],
        mode="markers",
        marker = dict(
            size=data["distance"],
            color=data["ascent"],
        ),
        hovertemplate='<b>{name}</b>:{name}<p><b>{route_name}</b>:{route_name}<p><b>{distance}</b>:{distance}<p><b>{time_min}</b>:{time_min}<p><b>{time_max}</b>:{time_max}<p><b>{ascent}</b>:{ascent}<p><b>{start_grid_ref}</b>:{start_grid_ref}<p><b>{munros_climbed}</b>:{munros_climbed}<p><b>{start_lat}</b>:{start_lat}<p><b>{start_lon}</b>:{start_lon}<p><b>{rating}</b>:{rating}<p><b>{grade}</b>:{grade}<p><b>{bog_factor}</b>:{bog_factor}<p><b>{route_page_link}</b>:{route_page_link}'
    )
))

fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=go.layout.mapbox.Center(
           **MAP_CENTER,
        ),
        zoom=6.5
    )
)
# fig.update_traces(cluster=dict(enabled=True))
fig.show()

# +
import folium
import folium.plugins

def dict_to_html(d):
    text = ''
    text += '<p>'.join(['<b>{0}</b>: {1}'.format(k, v) for k, v in d.items()])
    return text

def route_map(df):
    latitude = 57.2
    longitude = -4.5

    scotland_map = folium.Map(location=[latitude, longitude], zoom_start=7)

    routes = folium.plugins.MarkerCluster().add_to(scotland_map)
    tooltip_cols = df.columns
    # loop through the dataframe and add each data point to the mark cluster
    for lat, lng, label, data_dict in zip(df.start_lat, df.start_lon, df.route_name, df[tooltip_cols].to_dict(orient="records")):
        folium.Marker(
        location=[lat, lng],
        tooltip=label,
        popup=dict_to_html(data_dict)
        ).add_to(routes)

    # show map
    display(scotland_map)

route_map(data)
# -


