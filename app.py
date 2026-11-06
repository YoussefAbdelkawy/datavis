import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, ctx, dcc, html

from charts.map_heat import MAP_NOTE, make_map
from charts.q1_q2 import Q1_NOTE, make_q1
from charts.q3_q4 import Q3_NOTE, make_q3
from charts.q5_q6 import Q5_NOTE, make_q5
from charts.q7_q8 import Q7_NOTE, make_q7
from charts.shared import BOROUGHS, PERSONS, WORK_TYPES, YEARS
from search import parse_search

# (id, question, chart function, filter note) for each question chart merged so far
QUESTIONS = [
    ("q1", "Q1. Do squares with lots of street work already have more crashes, even in months with no work?", make_q1, Q1_NOTE),
    ("q3", "Q3. Which work type changes crashes the most within the same square?", make_q3, Q3_NOTE),
    ("q5", "Q5. Which ZIPs have the most \"permanent\" sidewalk sheds (still up, > 2 years)?", make_q5, Q5_NOTE),
    ("q7", "Q7. Which contributing factors become more common near work?", make_q7, Q7_NOTE),
]
CHART_MAKERS = [make_map] + [maker for _, _, maker, _ in QUESTIONS]
CHART_IDS = ["map"] + [chart_id for chart_id, _, _, _ in QUESTIONS]


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

charts = html.Div([
    dbc.Row(dbc.Col(chart_card("map", "Where are the street-work sites and the crashes?", MAP_NOTE)), className="mb-4"),
    dbc.Row([dbc.Col(chart_card(chart_id, heading, note), className="mb-4")
             for chart_id, heading, _, note in QUESTIONS]),
])

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="Are construction zones crash zones?")
server = app.server
app.layout = dbc.Container([
    html.H1("Are construction zones crash zones?", className="mt-4"),
    html.P("NYC street-work permits (DOB NOW) × motor vehicle crashes, 2022–2026.", className="lead text-muted"),
    filters, charts,
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
    app.run(debug=True)
