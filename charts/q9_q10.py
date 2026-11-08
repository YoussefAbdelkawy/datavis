import pandas as pd
import plotly.express as px

from charts.shared import NO_WORK, WORK, WORK_COLOURS, chart_note, empty_figure, filter_crashes, label_work, style

Q9_NOTE = chart_note("Year, Work type, Person injured", "Borough (the selected borough is highlighted)")
Q10_NOTE = chart_note("Person injured", "Borough, Year, Work type (it is a borough comparison over time)")


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


def make_q10(f):
    rows = filter_crashes({**f, "borough": "All", "year": "All"})
    rows = rows[rows.borough.notna()]
    if rows.empty:
        return empty_figure("Crashes vs own 2024 average")
    # monthly crashes, Manhattan vs the rest, each as % of its own 2024 average
    monthly = rows.groupby(["month", rows.borough == "MANHATTAN"]).size().unstack()
    monthly = monthly / monthly[monthly.index.year == 2024].mean() * 100
    monthly.columns = ["Other boroughs", "Manhattan"]
    yearly = monthly.groupby(monthly.index.year).mean()
    manhattan, others = yearly.Manhattan, yearly["Other boroughs"]
    subtitle = (f"2025 / 2026: Manhattan {manhattan[2025]:.1f}% / {manhattan[2026]:.1f}%"
                f" · others {others[2025]:.1f}% / {others[2026]:.1f}%")
    long = monthly.reset_index().melt(id_vars="month", var_name="area", value_name="pct")
    fig = px.line(
        long, x="month", y="pct", color="area",
        color_discrete_map={"Manhattan": WORK, "Other boroughs": NO_WORK},
        title="Crashes vs own 2024 average",
        labels={"month": "Month", "pct": "Crashes (% of own 2024 average)", "area": ""},
    )
    fig.add_vline(pd.Timestamp("2025-01-05").timestamp() * 1000, line_color="white", line_dash="dash",
                  annotation_text="Congestion pricing")
    fig.update_xaxes(range=[long.month.min(), long.month.max()])
    return style(fig, subtitle)
