import pandas as pd
from plotly import express as px
from plotly import graph_objects as go


def _create_map_fig(
    routes_df: pd.DataFrame, highlight_points: list[tuple[float, float, str]] | None = None
) -> px.scatter_mapbox:
    map_fig = px.scatter_mapbox(
        routes_df,
        lat="start_lat",
        lon="start_lon",
        color="ascent",
        size="distance",
        hover_name="route_name",
        hover_data=PLOT_COLUMNS,
        custom_data=["route_page_link"],
        mapbox_style="open-street-map",
        center=MAP_CENTER,
        zoom=6,
        height=700,
        color_continuous_scale=px.colors.sequential.Reds,
    )
    if highlight_points:
        for point in highlight_points:
            map_fig.add_trace(
                go.Scattermapbox(
                    lat=[point[0]],
                    lon=[point[1]],
                    marker=dict(size=15, color="teal"),
                    name=point[2],
                )
            )

    map_fig.update_layout(
        coloraxis_colorbar=dict(
            yanchor="top",
            y=1,
            x=0,
            ticks="inside",
        )
    )
    return map_fig


TABLE_COLUMNS = [
    "route_name",
    "distance",
    "commute_time",
    "total_time",
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

PLOT_COLUMNS = list(set(TABLE_COLUMNS) - {"route_page_link", "commute_time", "total_time"})

MAP_CENTER = {"lat": 57.3, "lon": -4.28}
