import folium
import folium.plugins
import pandas as pd
import solara

zoom = solara.reactive(7)
center = solara.reactive((57.2, -4.5))
bounds = solara.reactive(None)


data = pd.read_csv("../data/all_routes_add_features.csv")


def dict_to_html(d):
    text = ""
    text += "<p>".join([f"<b>{k}</b>: {v}" for k, v in d.items()])
    return text


@solara.component
def Page():
    lat, long = center.value
    scotland_map = folium.Map(location=[lat, long], zoom_start=zoom.value)

    routes = folium.plugins.MarkerCluster().add_to(scotland_map)
    tooltip_cols = data.columns
    # loop through the dataframe and add each data point to the mark cluster
    for lat, lng, label, data_dict in zip(
        data.start_lat, data.start_lon, data.route_name, data[tooltip_cols].to_dict(orient="records")
    ):
        folium.Marker(location=[lat, lng], tooltip=label, popup=dict_to_html(data_dict)).add_to(routes)
    scotland_map


Page()
