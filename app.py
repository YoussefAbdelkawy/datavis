import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html

from charts.q1_q2 import Q1_NOTE, make_q1
from charts.shared import BOROUGHS, PERSONS, WORK_TYPES, YEARS

# (id, question, chart function, filter note) for each question chart merged so far
QUESTIONS = [
    ("q1", "Q1. Do squares with lots of street work already have more crashes, even in months with no work?", make_q1, Q1_NOTE),
]
CHART_MAKERS = [maker for _, _, maker, _ in QUESTIONS]
CHART_IDS = [chart_id for chart_id, _, _, _ in QUESTIONS]


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


@app.callback(
    [Output(chart_id, "figure") for chart_id in CHART_IDS],
    Input("generate", "n_clicks"),
    State("borough", "value"), State("year", "value"), State("work", "value"), State("person", "value"),
)
def update(n_clicks, borough, year, work, person):
    f = {"borough": borough, "year": year, "work": work, "person": person}
    # every chart is rebuilt with the same four filters
    return [make_chart(f) for make_chart in CHART_MAKERS]


if __name__ == "__main__":
    app.run(debug=True)
