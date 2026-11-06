import plotly.express as px

from charts.shared import WORK_COLOURS, chart_note, filter_crashes, label_work, style

Q9_NOTE = chart_note("Year, Work type, Person injured", "Borough (the selected borough is highlighted)")


def make_q9(f):
    rows = label_work(filter_crashes({**f, "borough": "All"}), f["work"])
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
