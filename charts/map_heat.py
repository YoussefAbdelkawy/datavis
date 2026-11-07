import pandas as pd
import plotly.express as px

from charts.shared import WORK, chart_note, empty_figure, filter_crashes, filter_jobs, style

MAP_NOTE = chart_note("Borough, Year, Work type, Person injured")

# map centre (lat, lon) and zoom for each borough choice
MAP_VIEW = {
    "All": (40.70, -73.95, 9.3),
    "MANHATTAN": (40.78, -73.97, 11),
    "BROOKLYN": (40.65, -73.95, 10.6),
    "QUEENS": (40.71, -73.83, 10.3),
    "BRONX": (40.85, -73.87, 10.8),
    "STATEN ISLAND": (40.58, -74.15, 10.8),
}


def make_map(f):
    sites = filter_jobs(f)
    crash_rows = filter_crashes(f)
    # with a work type chosen, show only crashes where that type was active
    if f["work"] != "All":
        crash_rows = crash_rows[crash_rows.work_types.str.contains(f["work"], regex=False)]
    if sites.empty and crash_rows.empty:
        return empty_figure("Street-work sites and crashes")
    # random sample keeps the map fast
    sites = sites.sample(min(3000, len(sites)), random_state=0)
    crash_rows = crash_rows.sample(min(3000, len(crash_rows)), random_state=0)
    points = pd.concat([
        pd.DataFrame({"lat": sites.lat, "lon": sites.lon, "layer": "Street-work site"}),
        pd.DataFrame({"lat": crash_rows.lat, "lon": crash_rows.lon, "layer": "Crash"}),
    ])
    lat, lon, zoom = MAP_VIEW[f["borough"]]
    fig = px.scatter_map(
        points, lat="lat", lon="lon", color="layer",
        color_discrete_map={"Street-work site": WORK, "Crash": "#FFFFFF"},
        center={"lat": lat, "lon": lon}, zoom=zoom, opacity=0.6, height=600,
        map_style="carto-darkmatter", title="Street-work sites and crashes",
    )
    return style(fig, f"Random sample of up to 3,000 of each: {len(sites):,} sites, {len(crash_rows):,} crashes shown")
