import plotly.express as px
import plotly.graph_objects as go

from charts.shared import NO_WORK, WORK, chart_note, empty_figure, filter_jobs, square_differences, style

Q3_NOTE = chart_note("Borough, Year, Person injured", "Work type (the selected type is highlighted, not filtered)")
Q4_NOTE = chart_note("Borough, Year, Work type", "Person injured (permits have no injuries)")


def make_q3(f):
    diff = square_differences(f)
    if diff.empty:
        return empty_figure("Same-square change by work type")
    # each square counts under its most common work type
    q3 = diff.groupby(level="main_type", observed=True).agg(["mean", "count"]).sort_values("mean").reset_index()
    colours = [WORK if f["work"] in ("All", t) else NO_WORK for t in q3.main_type]
    fig = px.bar(
        q3, x="main_type", y="mean", hover_data={"count": True},
        title="Same-square change by work type",
        labels={"main_type": "Main work type of the square", "mean": "Work minus no work (crashes/month)", "count": "Squares"},
    )
    fig.update_traces(marker_color=colours)
    fig.add_hline(0, line_color="white", line_dash="dash")
    return style(fig, "Average per square, grouped by its main work type")


def make_q4(f):
    rows = filter_jobs(f)
    if rows.empty:
        return empty_figure("How long each work type lasts")
    # one box per work type, from precomputed stats (keeps the page light)
    # reindex keeps the five quantile columns in a fixed order
    stats = rows.groupby("work_type", observed=True).days.quantile([0, 0.25, 0.5, 0.75, 1]).unstack()
    stats = stats.reindex(columns=[0, 0.25, 0.5, 0.75, 1]).sort_values(0.5)
    fig = go.Figure(go.Box(
        x=stats.index, lowerfence=stats[0], q1=stats[0.25], median=stats[0.5],
        q3=stats[0.75], upperfence=stats[1], marker_color=WORK, name="",
    ))
    fig.update_layout(title="How long each work type lasts")
    fig.update_xaxes(title_text="Work type")
    fig.update_yaxes(title_text="Job duration (days, log scale)", type="log")
    return style(fig, "Box = middle 50%, line = median, whiskers = shortest to longest")
