import plotly.express as px

from charts.shared import NO_WORK, WORK, chart_note, square_differences, style

Q3_NOTE = chart_note("Borough, Year, Person injured", "Work type (the selected type is highlighted, not filtered)")


def make_q3(f):
    diff = square_differences(f)
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
