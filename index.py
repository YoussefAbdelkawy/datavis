# Vercel entrypoint: Vercel looks for a Flask app named `app`.
# In app.py, `app` is the Dash object, so we hand Vercel its Flask server instead.
from app import server as app
