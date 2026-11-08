import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc, html

from charts.map_heat import HEAT_NOTE, MAP_NOTE, make_heatmap, make_map
from charts.q1_q2 import Q1_NOTE, Q2_NOTE, make_q1, make_q2
from charts.q3_q4 import Q3_NOTE, Q4_NOTE, make_q3, make_q4
from charts.q5_q6 import Q5_NOTE, Q6_NOTE, make_q5, make_q6
from charts.q7_q8 import Q7_NOTE, Q8_NOTE, make_q7, make_q8
from charts.q9_q10 import Q9_NOTE, Q10_NOTE, make_q9, make_q10
from charts.shared import BOROUGHS, PERSONS, WORK_TYPES, YEARS
from search import parse_search

GITHUB_URL = "https://github.com/YoussefAbdelkawy/datavis"

# (id, question, chart function, filter note) for the 10 question charts
QUESTIONS = [
    ("q1", "Q1. Do squares with lots of street work already have more crashes, even in months with no work?", make_q1, Q1_NOTE),
    ("q2", "Q2. Comparing a square with itself, how different are its work months from its no-work months?", make_q2, Q2_NOTE),
    ("q3", "Q3. Which work type changes crashes the most within the same square?", make_q3, Q3_NOTE),
    ("q4", "Q4. How long does each work type really last?", make_q4, Q4_NOTE),
    ("q5", "Q5. Which ZIPs have the most \"permanent\" sidewalk sheds (still up, > 2 years)?", make_q5, Q5_NOTE),
    ("q6", "Q6. Near street work, are the injured more often pedestrians or cyclists?", make_q6, Q6_NOTE),
    ("q7", "Q7. Which contributing factors become more common near work?", make_q7, Q7_NOTE),
    ("q8", "Q8. Do crashes near work peak during working hours?", make_q8, Q8_NOTE),
    ("q9", "Q9. Are trucks a bigger share of crashes near work, in every borough?", make_q9, Q9_NOTE),
    ("q10", "Q10. Did Manhattan crashes drop after congestion pricing (5 Jan 2025) vs other boroughs?", make_q10, Q10_NOTE),
]
CHART_MAKERS = [make_map] + [maker for _, _, maker, _ in QUESTIONS] + [make_heatmap]
CHART_IDS = ["map"] + [chart_id for chart_id, _, _, _ in QUESTIONS] + ["heat"]

STORY = [
    ("Question", "Is the street around street work (sidewalk sheds, scaffolds, fences, demolition) more dangerous "
     "while the work is active? Sheds and fences push people off the sidewalk and block drivers' view, "
     "and some sheds stay up for years."),
    ("Key findings", "Who gets hurt changes: near active work, pedestrians and cyclists are 41% of the injured, "
     "vs 33% without (Q6). The number of crashes does not: squares that get a lot of work were already riskier "
     "in their no-work months (Q1), and the same square shows no overall change with work (Q2). "
     "No work type stands out (Q3), and Manhattan shows no relative drop after congestion pricing (Q10)."),
    ("Limitations", "No exposure data (traffic or foot counts), so more crashes may just mean more people. "
     "Permit dates say when work is allowed, not when it really happened. "
     "This is association, not cause."),
    ("Benefit to NYC", "DOT and DOB can target safety by how risky a place is, not by permit count alone, "
     "and protect pedestrians and cyclists first around active sites (covered walkways, marked bike detours). "
     "DOB can follow up on sheds standing for years in ZIPs like 10025 and 10452."),
]


def dropdown(dropdown_id, label, options):
    # "All" first, then the real values; options are (value, label) pairs
    choices = [{"label": "All", "value": "All"}] + [{"label": text, "value": value} for value, text in options]
    return dbc.Col([dbc.Label(label), dcc.Dropdown(id=dropdown_id, options=choices, value="All", clearable=False)], xs=12, md=3)


def chart_card(chart_id, heading, note):
    return dbc.Card(dbc.CardBody([
        html.H5(heading),
        dcc.Graph(id=chart_id),
        html.Small(note, className="text-muted"),
    ]), className="mb-4 h-100")


filters = dbc.Card(dbc.CardBody([
    dbc.Input(id="search", type="text",
              placeholder="Search, e.g. \"Brooklyn 2023 sidewalk shed pedestrians\", then press Enter"),
    html.Small(id="understood", className="text-muted"),
    dbc.Row([
        dropdown("borough", "Borough", [(b, b.title()) for b in BOROUGHS]),
        dropdown("year", "Year", [(y, y) for y in YEARS]),
        dropdown("work", "Work type", [(w, w) for w in WORK_TYPES]),
        dropdown("person", "Person injured", [(p, p) for p in PERSONS]),
    ], className="mt-3 g-3"),
    html.Div(dbc.Button("Generate Report", id="generate", color="warning", size="lg", className="mt-4 px-5"),
             className="text-center"),
]), className="mb-4")

charts = dcc.Loading([
    dbc.Row(dbc.Col(chart_card("map", "Where are the street-work sites and the crashes?", MAP_NOTE)), className="mb-4"),
    dbc.Row([dbc.Col(chart_card(chart_id, heading, note), xs=12, lg=6, className="mb-4")
             for chart_id, heading, _, note in QUESTIONS]),
    dbc.Row(dbc.Col(chart_card("heat", "At what hour and weekday do crashes happen near active work?", HEAT_NOTE))),
], type="circle")

story = html.Div([html.H2("Story", className="mt-5 mb-3")] + [
    dbc.Card(dbc.CardBody([html.H5(title), html.P(text, className="mb-0")]), className="mb-3")
    for title, text in STORY
])

footer = html.Footer([
    html.Hr(),
    html.P([
        "Data: ",
        html.A("DOB NOW: Build – Approved Permits", href="https://data.cityofnewyork.us/d/rbx6-tga4"), " · ",
        html.A("Motor Vehicle Collisions – Crashes", href="https://data.cityofnewyork.us/d/h9gi-nx95"), " · ",
        html.A("Code on GitHub", href=GITHUB_URL),
    ], className="text-muted small"),
], className="my-4")

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="Are construction zones crash zones?")
server = app.server
app.layout = dbc.Container([
    html.H1("Are construction zones crash zones?", className="mt-4"),
    html.P("NYC street-work permits (DOB NOW) × motor vehicle crashes, 2022–2026.", className="lead text-muted"),
    filters, charts, story, footer,
], fluid="lg")


def describe(found, ignored):
    # e.g. "Understood: Brooklyn · 2023 · Sidewalk Shed — ignored: near, school"
    parts = [found[name].title() if name == "borough" else found[name]
             for name in ["borough", "year", "work", "person"] if name in found]
    text = "Understood: " + (" · ".join(parts) or "nothing")
    if ignored:
        text += " — ignored: " + ", ".join(ignored)
    return text


@app.callback(
    [Output(chart_id, "figure") for chart_id in CHART_IDS]
    + [Output("borough", "value"), Output("year", "value"), Output("work", "value"), Output("person", "value"),
       Output("understood", "children")],
    Input("generate", "n_clicks"),
    Input("search", "n_submit"),
    State("borough", "value"), State("year", "value"), State("work", "value"), State("person", "value"),
    State("search", "value"),
)
def update(n_clicks, n_submit, borough, year, work, person, text):
    f = {"borough": borough, "year": year, "work": work, "person": person}
    understood = ""
    # search: fill the dropdowns with what the text mentions, keep the rest
    if ctx.triggered_id == "search":
        found = parse_search(text or "")
        ignored = found.pop("ignored")
        f.update(found)
        understood = describe(found, ignored)
    figures = [make_chart(f) for make_chart in CHART_MAKERS]
    return figures + [f["borough"], f["year"], f["work"], f["person"], understood]


if __name__ == "__main__":
    app.run(debug=False)
