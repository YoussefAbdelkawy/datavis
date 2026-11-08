from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# load the exported data once, when the app starts
DATA = Path(__file__).resolve().parent.parent / "data"
crashes = pd.read_parquet(DATA / "crashes.parquet")
jobs = pd.read_parquet(DATA / "jobs.parquet")
squares = pd.read_parquet(DATA / "squares.parquet")


def add_job_crashes(jobs, crashes):
    # for each job: crashes in its ~100 m square during the months it was running
    # (same square id as the notebook: lat/lon rounded to 3 decimals)
    def square_id(rows):
        return rows.lat.round(3).astype(str) + "," + rows.lon.round(3).astype(str)

    crashes = crashes.assign(cell=square_id(crashes), any_crash=1,
                             ped_crash=(crashes.ped_inj > 0).astype(int),
                             cyc_crash=(crashes.cyc_inj > 0).astype(int),
                             mot_crash=(crashes.mot_inj > 0).astype(int),
                             injured=crashes.ped_inj + crashes.cyc_inj + crashes.mot_inj)
    counts = ["any_crash", "ped_crash", "cyc_crash", "mot_crash", "ped_inj", "injured"]
    per_month = crashes.groupby(["cell", "month"])[counts].sum()

    # one row per job and month it was running (start month to end month, both included)
    start = jobs.start.dt.to_period("M")
    months = (jobs.end.dt.to_period("M") - start).apply(lambda gap: gap.n) + 1
    job_months = pd.DataFrame({
        "job": jobs.index.repeat(months),
        "cell": square_id(jobs).repeat(months).values,
        "month": (start.repeat(months) + jobs.index.repeat(months).to_series().groupby(level=0).cumcount().values)
        .dt.to_timestamp().values,
    })
    # a month with no crash in the square counts as 0
    joined = job_months.join(per_month, on=["cell", "month"]).fillna(0)
    totals = joined.groupby("job")[counts].sum()
    return jobs.assign(months=months.values).join(totals)


jobs = add_job_crashes(jobs, crashes)

BOROUGHS = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
YEARS = ["2022", "2023", "2024", "2025", "2026"]
WORK_TYPES = sorted(jobs.work_type.unique())
PERSONS = ["Pedestrian", "Cyclist", "Motorist"]

WORK = "#F28E2B"
NO_WORK = "#9AA0A6"
WORK_COLOURS = {"work": WORK, "no work": NO_WORK}
PERSON_COLOURS = {"Pedestrian": "#4E79A7", "Cyclist": "#59A14F", "Motorist": "#E15759"}

# injury column (crashes) and column prefix (squares) for each person filter
PERSON_COLUMN = {"Pedestrian": "ped_inj", "Cyclist": "cyc_inj", "Motorist": "mot_inj"}
PERSON_PREFIX = {"All": "", "Pedestrian": "ped_", "Cyclist": "cyc_", "Motorist": "mot_"}
# per-job crash column for each person filter (crashes where that person type was injured)
JOB_CRASH_COLUMN = {"All": "any_crash", "Pedestrian": "ped_crash", "Cyclist": "cyc_crash", "Motorist": "mot_crash"}


def filter_crashes(f):
    # keep only crashes matching borough, year and person ("All" = no filter)
    rows = crashes
    if f["borough"] != "All":
        rows = rows[rows.borough == f["borough"]]
    if f["year"] != "All":
        rows = rows[rows.year == int(f["year"])]
    if f["person"] != "All":
        rows = rows[rows[PERSON_COLUMN[f["person"]]] > 0]
    return rows


def label_work(rows, work_type):
    # only squares that have street work at some point (the notebook's `near`)
    rows = rows[rows.work_square]
    # "work" = that work type was active in the square that month, "no work" = nothing active
    if work_type == "All":
        is_work = rows.active
    else:
        is_work = rows.work_types.str.contains(work_type, regex=False)
    rows = rows[is_work | ~rows.active]
    return rows.assign(work=is_work.map({True: "work", False: "no work"}))


def filter_jobs(f):
    # keep only street-work jobs matching borough, year (of start) and work type
    rows = jobs
    if f["borough"] != "All":
        rows = rows[rows.borough == f["borough"]]
    if f["year"] != "All":
        rows = rows[rows.year == int(f["year"])]
    if f["work"] != "All":
        rows = rows[rows.work_type == f["work"]]
    return rows


def square_totals(f):
    # sum each square over the chosen years; crash counts for the chosen person type
    rows = squares
    if f["borough"] != "All":
        rows = rows[rows.borough == f["borough"]]
    if f["year"] != "All":
        rows = rows[rows.year == int(f["year"])]
    prefix = PERSON_PREFIX[f["person"]]
    columns = ["work_months", "nowork_months", prefix + "crashes_work", prefix + "crashes_nowork"]
    totals = rows.groupby(["cell", "main_type"], observed=True)[columns].sum()
    totals.columns = ["work_months", "nowork_months", "crashes_work", "crashes_nowork"]
    return totals


def square_differences(f):
    # same square: avg crashes in work months minus no-work months (>= 6 months of each)
    totals = square_totals(f)
    fair = totals[(totals.work_months >= 6) & (totals.nowork_months >= 6)]
    return fair.crashes_work / fair.work_months - fair.crashes_nowork / fair.nowork_months


def style(fig, subtitle=""):
    # shared dark look with transparent backgrounds
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font_size=15,
        title_subtitle_text=subtitle,
        title_subtitle_font_size=11,
        legend_title_text="",
        margin=dict(l=10, r=10, t=70, b=10),
    )
    return fig


def chart_note(used, ignored=""):
    text = "Filters used: " + used + "."
    if ignored:
        text += " Ignored: " + ignored + "."
    return text


def empty_figure(title, message="No data for this filter combination"):
    # blank chart with a centred message, same dark style
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font_size=14)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style(fig.update_layout(title=title))
