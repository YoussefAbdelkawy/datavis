import pandas as pd
import plotly.express as px

from charts.shared import (JOB_CRASH_COLUMN, NO_WORK, WORK, chart_note, empty_figure, filter_jobs,
                           square_differences, style)

Q3_NOTE = chart_note("Borough, Year, Person injured", "Work type (the selected type is highlighted, not filtered)")
Q4_NOTE = chart_note("Borough, Year (job start), Work type (that type vs all others), Person injured")


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


# job length bands; each point sits at the median length of its band
DURATION_BANDS = [0, 90, 180, 365, 730, 10_000]
DURATION_LABELS = ["< 3 months", "3–6 months", "6–12 months", "1–2 years", "> 2 years"]
# 8 work types grouped into 4 families, so the chart keeps to 4 lines (lecture 4: max 4–5 lines)
FAMILIES = {
    "Sidewalk Shed": "Sheds & scaffolds", "Supported Scaffold": "Sheds & scaffolds",
    "Suspended Scaffold": "Sheds & scaffolds", "Construction Fence": "Fences",
    "General Construction": "Building & demolition", "Full Demolition": "Building & demolition",
    "Earth Work": "Ground work", "Foundation": "Ground work",
}
FAMILY_COLOURS = {"Sheds & scaffolds": WORK, "Fences": "#4E79A7",
                  "Building & demolition": "#E15759", "Ground work": "#59A14F"}


def make_q4(f):
    rows = filter_jobs({**f, "work": "All"})
    if rows.empty:
        return empty_figure("Crashes per month vs job length")
    # line per family, or the selected work type vs every other job
    if f["work"] == "All":
        group = rows.work_type.map(FAMILIES).astype(str)
        colours = FAMILY_COLOURS
    else:
        group = rows.work_type.astype(str).where(rows.work_type == f["work"], "Other work types")
        colours = {f["work"]: WORK, "Other work types": NO_WORK}
    band = pd.cut(rows.days, DURATION_BANDS, labels=DURATION_LABELS)
    crashes = rows[JOB_CRASH_COLUMN[f["person"]]]
    # crashes per month in the job's square while it ran = total crashes / total job months
    q4 = (pd.DataFrame({"group": group, "band": band, "days": rows.days, "crashes": crashes, "months": rows.months})
          .groupby(["group", "band"], observed=True)
          .agg(days=("days", "median"), crashes=("crashes", "sum"), months=("months", "sum"), jobs=("days", "size"))
          .reset_index())
    q4 = q4[q4.jobs >= 30]  # fewer than 30 jobs is too noisy to plot
    if q4.empty:
        return empty_figure("Crashes per month vs job length")
    q4["rate"] = q4.crashes / q4.months
    fig = px.line(
        q4, x="days", y="rate", color="group", markers=True, log_x=True,
        color_discrete_map=colours, hover_data={"band": True, "jobs": ":,", "days": True},
        title="Crashes per month vs job length",
        labels={"days": "Job length (median days in band, log scale)", "rate": "Crashes per month in the square",
                "group": "", "band": "Length band", "jobs": "Jobs"},
    )
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(tickvals=[10, 30, 100, 300, 1000])
    return style(fig, "Each point = one length band (≥ 30 jobs); crashes in the job's square while it ran")
