import plotly.express as px

from charts.shared import (NO_WORK, PERSON_COLOURS, PERSON_PREFIX, WORK, chart_note, empty_figure, filter_crashes,
                           label_work, squares, style)

Q5_NOTE = chart_note("Person injured", "Borough, Year (it compares Manhattan with the rest over time), Work type (per-square totals)")
Q6_NOTE = chart_note("Borough, Year, Work type", "Person injured (the chart is the person split)")


def make_q5(f):
    # same-square gap per year: crashes/month in work months minus no-work months
    prefix = PERSON_PREFIX[f["person"]]
    rows = squares[(squares.work_months >= 3) & (squares.nowork_months >= 3)]  # >= 3 months of each that year
    gap = rows[prefix + "crashes_work"] / rows.work_months - rows[prefix + "crashes_nowork"] / rows.nowork_months
    area = (rows.borough == "MANHATTAN").map({True: "Manhattan", False: "Other boroughs"})
    q5 = gap.groupby([area, rows.year]).agg(["mean", "count"]).reset_index()
    q5.columns = ["area", "year", "gap", "squares"]
    q5["year"] = q5.year.astype(str)
    # grouped columns (lecture 4 chooser: over time, few periods, few categories -> column chart)
    fig = px.bar(
        q5, x="year", y="gap", color="area", barmode="group",
        color_discrete_map={"Manhattan": WORK, "Other boroughs": NO_WORK},
        hover_data={"squares": ":,"},
        title="Extra crashes in work months, Manhattan vs other boroughs",
        labels={"year": "Year", "gap": "Extra crashes per month when work is on", "area": "", "squares": "Squares"},
    )
    fig.add_hline(0, line_color="white", line_dash="dash")
    # congestion pricing started 5 Jan 2025: line between the 2024 and 2025 columns
    fig.add_vline(2.5, line_color="white", line_dash="dot", annotation_text="Congestion pricing")
    return style(fig, "Same square: crashes/month in work months minus no-work months (above 0 = more crashes with work)")


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
