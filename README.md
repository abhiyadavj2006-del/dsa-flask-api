# DSA Problems API — Flask REST API

A shipped Flask project for Abhi's real data: the **42 problems** from his live
DSA practice site (C 24, C++ 15, Python 3 — titles and languages copied from
https://abhiproblems.dpdns.org/problems-site/ on 9 Nov 2026) plus the
Hackathon Rivals leaderboard (Season 2026: 2 teams / 2 colleges, 1 entry at
27 pts).

## Why this exists

The Axe Consultancy Python Developer internship (Internshala, apply by
**12 Nov 2026**, ₹20,000–30,000/month) lists Python, Django, Flask, MySQL,
SQL, REST API, Git, Data Structures and OOP. Abhi had shipped Python APIs
(clude) and MySQL work, but **no Flask/Django project yet** — so the Axe
application draft honestly said so. This project closes the Flask half
before the deadline, in about a day: build it, push it to GitHub, deploy it
on Railway (same account already running tracker + clude), then update the
application answer to say Flask is shipped.

Django is still honestly unshipped — do not claim it.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/api/stats` | total 42, counts by language, teams/colleges |
| GET | `/api/problems?q=linked+list&language=C` | search + filter |
| GET | `/api/problems/<id>` | one problem, 404 if missing |
| POST | `/api/problems` | add a problem (400 missing fields, 409 duplicate slug) |
| GET | `/api/leaderboard` | Hackathon Rivals leaderboard |

Storage is SQLite via SQL in `ProblemRepository` (`app.py`); swap
`DATABASE_PATH` / the connection for MySQL later — the SQL is standard
enough to port, and the MySQL migration labs already cover that move.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python test_api.py   # 7 tests, all should pass
python app.py        # http://localhost:5000/api/stats
```

## Deploy (Railway, free trial — no card)

1. Push this folder to a new GitHub repo, e.g. `dsa-flask-api`.
2. Railway → New Project → Deploy from GitHub → pick the repo.
   Start command is in `Procfile` (`gunicorn app:app`); Railway sets `PORT`.
3. Check `https://<your-app>.up.railway.app/api/stats` — expect
   `total_problems: 42`.
4. Note: the Railway trial allows only **one** custom domain and tracker
   already uses it, so this ships on the Railway URL, not a subdomain.

## Next step after shipping

Update the Axe "Why should you be hired?" answer: replace
"Django and Flask are the listed skills I haven't shipped in yet" with
"I shipped a Flask REST API (DSA Problems API, live on Railway) serving
my 42-problem DSA site over SQL-backed endpoints, with search, filters
and a leaderboard API." Django stays unclaimed.
