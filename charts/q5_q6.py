import plotly.express as px

from charts.shared import PERSON_COLOURS, WORK, chart_note, empty_figure, filter_crashes, jobs, label_work, style

Q5_NOTE = chart_note("Borough", "Year, Work type, Person injured (sidewalk sheds standing today)")
Q6_NOTE = chart_note("Borough, Year, Work type", "Person injured (the chart is the person split)")


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


def make_q6(f):
    rows = label_work(filter_crashes({**f, "person": "All"}), f["work"])
    if rows.empty:
        return empty_figure("Who is injured, work vs no work")
    # share of injured people who are pedestrians, cyclists, motorists, work vs no work
    injured = rows.groupby("work")[["ped_inj", "cyc_inj", "mot_inj"]].sum()
    # drop a group with crashes but nobody injured (its shares would be 0 / 0)
    injured = injured[injured.sum(axis=1) > 0]
    if injured.empty:
        return empty_figure("Who is injured, work vs no work")
    injured.columns = ["Pedestrian", "Cyclist", "Motorist"]
    shares = injured.div(injured.sum(axis=1), axis=0) * 100
    walk_bike = (shares.Pedestrian + shares.Cyclist).round(0)
    subtitle = "Pedestrians + cyclists: " + " · ".join(f"{w} {v:.0f}%" for w, v in walk_bike.items())
    long = shares.reset_index().melt(id_vars="work", var_name="person", value_name="share")
    fig = px.bar(
        long, x="work", y="share", color="person", text_auto=".1f",
        color_discrete_map=PERSON_COLOURS, category_orders={"work": ["no work", "work"]},
        title="Who is injured, work vs no work",
        labels={"work": "Month in the square", "share": "% of people injured", "person": "Injured"},
    )
    return style(fig, subtitle)
