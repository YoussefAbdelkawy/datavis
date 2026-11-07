import plotly.express as px

from charts.shared import WORK, chart_note, empty_figure, jobs, style

Q5_NOTE = chart_note("Borough", "Year, Work type, Person injured (sidewalk sheds standing today)")


def make_q5(f):
    # sidewalk sheds still up at the end of the data (31 Oct 2026) and up for more than 2 years
    sheds = jobs[(jobs.work_type == "Sidewalk Shed") & (jobs.end == "2026-10-31") & (jobs.days > 730)]
    if f["borough"] != "All":
        sheds = sheds[sheds.borough == f["borough"]]
    if sheds.empty:
        return empty_figure("ZIPs with most sheds up > 2 years")
    top = sheds.zip_code.astype(str).value_counts().head(15).sort_values().reset_index()
    fig = px.bar(
        top, x="count", y="zip_code", orientation="h",
        title="ZIPs with most sheds up > 2 years",
        labels={"count": "Sheds still up after > 2 years", "zip_code": "ZIP code"},
    )
    fig.update_traces(marker_color=WORK)
    fig.update_yaxes(type="category")
    return style(fig, f"{len(sheds):,} sheds up > 2 years and still standing")
