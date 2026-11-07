import pandas as pd
import plotly.express as px

from charts.shared import NO_WORK, WORK, chart_note, empty_figure, filter_crashes, label_work, style

Q7_NOTE = chart_note("Borough, Year, Work type, Person injured")


def make_q7(f):
    rows = label_work(filter_crashes(f), f["work"])
    if rows.empty:
        return empty_figure("Factor share change near work")
    # share of crashes citing each factor, work minus no-work, in percentage points
    shares = pd.crosstab(rows.factor, rows.work, normalize="columns") * 100
    shares = shares.reindex(columns=["no work", "work"], fill_value=0)
    change = (shares["work"] - shares["no work"]).drop(["Unspecified", "Does Not Apply"], errors="ignore")
    top = change.loc[change.abs().nlargest(10).index].sort_values().reset_index(name="change")
    fig = px.bar(
        top, x="change", y="factor", orientation="h",
        title="Factor share change near work",
        labels={"change": "Work minus no work (percentage points)", "factor": ""},
    )
    fig.update_traces(marker_color=[WORK if c > 0 else NO_WORK for c in top.change])
    return style(fig, "Top 10; 'Unspecified' and 'Does Not Apply' left out")
