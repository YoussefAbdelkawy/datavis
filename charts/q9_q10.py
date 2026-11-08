import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from charts.shared import NO_WORK, WORK, WORK_COLOURS, chart_note, empty_figure, filter_crashes, jobs, label_work, style

Q9_NOTE = chart_note("Year, Work type, Person injured", "Borough (the selected borough is highlighted)")
Q10_NOTE = chart_note("Borough", "Year (a > 2-year shed spans several years), Work type (sheds only), Person injured (the right panel is the pedestrian share)")


def make_q9(f):
    rows = label_work(filter_crashes({**f, "borough": "All"}), f["work"])
    if rows.empty:
        return empty_figure("Truck share of crashes, by borough")
    # % of crashes where vehicle 1 is a truck, per borough and work / no work
    trucks = rows.assign(truck=rows.vehicle_group == "truck")
    q9 = (trucks.groupby(["borough", "work"], observed=True).truck.mean() * 100).reset_index()
    q9["borough"] = q9.borough.astype(str).str.title()
    fig = px.bar(
        q9, x="borough", y="truck", color="work", barmode="group",
        color_discrete_map=WORK_COLOURS, category_orders={"work": ["no work", "work"]},
        title="Truck share of crashes, by borough",
        labels={"borough": "Borough", "truck": "% of crashes with a truck (vehicle 1)", "work": ""},
    )
    # fade the other boroughs when one is selected
    if f["borough"] != "All":
        for trace in fig.data:
            trace.marker.opacity = [1 if b == f["borough"].title() else 0.3 for b in trace.x]
    return style(fig, "Squares with street work: work vs no-work months")


SHED_BANDS = [0, 182, 365, 730, 10_000]
SHED_LABELS = ["< 6 months", "6–12 months", "1–2 years", "> 2 years"]


def make_q10(f):
    sheds = jobs[jobs.work_type == "Sidewalk Shed"]
    if f["borough"] != "All":
        sheds = sheds[sheds.borough == f["borough"]]
    if sheds.empty:
        return empty_figure("Long-standing vs short-lived sheds")
    # per shed: crashes in its square while it stood; pooled over every shed in the band
    band = pd.cut(sheds.days, SHED_BANDS, labels=SHED_LABELS)
    q10 = sheds.groupby(band, observed=True)[["any_crash", "months", "ped_inj", "injured"]].sum()
    q10["rate"] = q10.any_crash / q10.months
    q10["ped_share"] = q10.ped_inj / q10.injured * 100
    q10["sheds"] = sheds.groupby(band, observed=True).size()
    q10 = q10.reset_index(names="band")
    colours = [WORK if b == "> 2 years" else NO_WORK for b in q10.band]
    # two panels side by side: the question asks about two measures
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.15)
    panels = [("rate", ".3f", "Crashes per month in the square"), ("ped_share", ".1f", "Pedestrians (% of injured)")]
    for col, (metric, fmt, axis_title) in enumerate(panels, start=1):
        fig.add_trace(go.Bar(
            x=q10.band, y=q10[metric], marker_color=colours, texttemplate="%{y:" + fmt + "}",
            textposition="outside", cliponaxis=False,
            customdata=q10.sheds, hovertemplate="%{x}: %{y:" + fmt + "}<br>%{customdata:,} sheds<extra></extra>",
        ), row=1, col=col)
        fig.update_yaxes(title_text=axis_title, rangemode="tozero", row=1, col=col)
    fig.update_layout(title="Long-standing vs short-lived sheds", showlegend=False)
    fig.update_xaxes(title_text="How long the shed stood")
    return style(fig, f"{len(sheds):,} sidewalk sheds; crashes in each shed's square while it stood")
