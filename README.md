# Are construction zones crash zones?

A one-page Dash site that links NYC street-work permits (DOB NOW: Build – Approved Permits)
with motor vehicle crashes, 2022–2026. Both go on the same ~100 m square × month grid;
a square-month is "work" if any street-work permit runs there that month.

**Live site:** https://datavis-4ioi.vercel.app/

Data: [DOB NOW permits](https://data.cityofnewyork.us/d/rbx6-tga4) ·
[Motor Vehicle Collisions – Crashes](https://data.cityofnewyork.us/d/h9gi-nx95)

## Run it locally
```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:8050.

The site reads the small parquet files in `data/`. To rebuild them, run `datavis.ipynb`
(its last cell, "Export data for the website", writes `data/`). The notebook downloads
`permits.csv` and `crashes.csv` on first run.

## How to use the page
- Pick Borough, Year, Work type and Person injured, then click **Generate Report**.
- Or type in the search box (e.g. `queens 2024 scaffold pedestrian`) and press Enter:
  it fills the dropdowns and builds the report.
- Under each chart, a note says which filters it uses and why it ignores the others.

## Deploy (Vercel, free)
1. Sign in at vercel.com with GitHub (Hobby plan, free).
2. Add New → Project → import this repo. Leave every setting on its default and click Deploy.
3. Vercel reads `pyproject.toml`: Python 3.13, the dependencies, and `index.py` as the entrypoint
   (it hands Vercel the Dash app's Flask server). `.vercelignore` keeps the notebook and raw CSVs out.
4. Open the `.vercel.app` link, pick a filter and click Generate Report to check every chart loads.

## Deploy (Render, alternative)
1. Render → New → Web Service → pick this repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:server`
4. Free plan. It sleeps when unused, so the first load takes about a minute.

## The 10 questions
1. Do squares with lots of street work already have more crashes, even in months with no work?
2. Comparing a square with itself, how different are its work months from its no-work months?
3. Which work type changes crashes the most within the same square?
4. How long does each work type really last?
5. Which ZIPs have the most "permanent" sidewalk sheds (still up, > 2 years)?
6. Near street work, are the injured more often pedestrians or cyclists?
7. Which contributing factors become more common near work?
8. Do crashes near work peak during working hours?
9. Are trucks a bigger share of crashes near work, in every borough?
10. Did Manhattan crashes drop after congestion pricing (5 Jan 2025) vs other boroughs?

## Code layout
```
app.py          layout + one callback
index.py        Vercel entrypoint (the Dash app's Flask server)
pyproject.toml  Python version, dependencies, Vercel entrypoint
search.py       parse_search: turns search text into filters
charts/
  shared.py     data loading, filters, colours, chart note helper
  q1_q2.py      Q1, Q2
  q3_q4.py      Q3, Q4
  q5_q6.py      Q5, Q6
  q7_q8.py      Q7, Q8
  q9_q10.py     Q9, Q10
  map_heat.py   map + hour × weekday heatmap
data/           parquet files exported from the notebook
```

## Team
5 members, 2 questions and 2 charts each. Built in 10 pull requests, 2 per member, merged in order
(see the Pull requests tab). The notebook's "Team contributions" section has the same split, and
its "Prompts used" section lists the AI prompts we used.

| Member | PRs | Questions (chart) | Data prep | Website |
|---|---|---|---|---|
| Yusef Wael Saeed | 1, 10 | Q1 (scatter), Q10 (line) | dataset choice, EDA, pre-integration cleaning, grid integration, post-integration cleaning, data export | base app, dropdowns, Generate Report, final story, README, deploy |
| Ibrahim Abdelshafy Ibrahim | 2, 3 | Q3 (bar), Q5 (horizontal bar) | work type per square-month, long-standing sheds by ZIP | dark dropdown style, search mode |
| Ibrahim Samer Alalamy | 4, 5 | Q7 (horizontal bar), Q9 (grouped bar) | contributing factors cleanup, vehicle type grouping | cross-domain map, story section and footer |
| Mostafa Amr Elsallamy | 6, 7 | Q2 (histogram), Q4 (box plot) | same-square comparison, job duration | empty-data message, hour × weekday heatmap |
| Hassan Hytham Ibrahim | 8, 9 | Q6 (100% stacked bar), Q8 (line) | injuries by person type, crash hour | loading spinner, responsive grid, map hover text |
