import pandas as pd
import plotly.express as px

from charts.shared import WORK, chart_note, empty_figure, filter_crashes, filter_jobs, label_work, style

MAP_NOTE = chart_note("Borough, Year, Work type, Person injured")
HEAT_NOTE = chart_note("Borough, Year, Work type, Person injured")

# map centre (lat, lon) and zoom for each borough choice
MAP_VIEW = {
    "All": (40.70, -73.95, 9.3),
    "MANHATTAN": (40.78, -73.97, 11),
    "BROOKLYN": (40.65, -73.95, 10.6),
    "QUEENS": (40.71, -73.83, 10.3),
    "BRONX": (40.85, -73.87, 10.8),
    "STATEN ISLAND": (40.58, -74.15, 10.8),
}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


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


def make_heatmap(f):
    rows = label_work(filter_crashes(f), f["work"])
    near_work = rows[rows.work == "work"]
    if near_work.empty:
        return empty_figure("When crashes happen near active street work")
    # crash counts per weekday x hour, in squares with active street work
    table = pd.crosstab(near_work.weekday, near_work.hour).reindex(index=range(7), columns=range(24), fill_value=0)
    table.index = WEEKDAYS
    fig = px.imshow(
        table, aspect="auto", color_continuous_scale="Oranges",
        title="When crashes happen near active street work",
        labels={"x": "Hour of day (0–23)", "y": "Weekday", "color": "Crashes"},
    )
    return style(fig, f"{len(near_work):,} crashes in squares with active work that month")
