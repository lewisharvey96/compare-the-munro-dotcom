import pandas as pd
import ipyleaflet
import solara

data = pd.read_csv("all_route_pages_data.csv")

data.head()

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


