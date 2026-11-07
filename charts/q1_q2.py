import pandas as pd
import plotly.express as px

from charts.shared import WORK, chart_note, empty_figure, square_differences, square_totals, style

Q1_NOTE = chart_note("Borough, Year, Person injured", "Work type (per-square totals)")
Q2_NOTE = chart_note("Borough, Year, Person injured", "Work type (per-square totals)")


def make_q1(f):
    totals = square_totals(f)
    # per square: share of months with work, avg crashes in its no-work months
    q1 = pd.DataFrame({
        "work_share": totals.work_months / (totals.work_months + totals.nowork_months),
        "no_work_crashes": totals.crashes_nowork / totals.nowork_months,
    }).dropna()
    if q1.empty:
        return empty_figure("Busy work squares already have more crashes")
    bins = q1.groupby(pd.cut(q1.work_share, [0, 0.25, 0.5, 0.75, 1]), observed=False).no_work_crashes.mean()
    subtitle = f"No-work crashes/month: {bins.iloc[0]:.3f} (≤ 25% work) → {bins.iloc[-1]:.3f} (> 75% work)"
    fig = px.scatter(
        q1, x="work_share", y="no_work_crashes", opacity=0.25,
        title="Busy work squares already have more crashes",
        labels={"work_share": "Share of months with street work", "no_work_crashes": "Crashes per month (no-work months)"},
    )
    fig.update_traces(marker=dict(size=4, color=WORK))
    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(range=[0, 2])
    return style(fig, subtitle)


def make_q2(f):
    diff = square_differences(f)
    if diff.empty:
        return empty_figure("Same square: work minus no-work months")
    subtitle = f"{len(diff):,} squares · mean {diff.mean():+.3f} · median {diff.median():.3f}"
    fig = px.histogram(
        x=diff, title="Same square: work minus no-work months",
        labels={"x": "Crashes per month: work minus no work"},
    )
    fig.update_traces(xbins=dict(start=-0.6, end=0.6, size=0.02), marker_color=WORK)
    fig.update_xaxes(range=[-0.6, 0.6])
    fig.update_yaxes(title_text="Number of squares")
    fig.add_vline(0, line_color="white", line_dash="dash")
    return style(fig, subtitle)
