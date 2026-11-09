"""DSA Problems API — Flask REST API for Abhi's 42-problem DSA practice site.

Built to close the one gap in the Axe Consultancy Python Developer
application (apply by 12 Nov 2026): a shipped Flask + SQL + REST API
project, using Abhi's real data — the 42 problems from his live DSA site
and the Hackathon Rivals leaderboard (1 entry, 27 pts).

Stack: Python, Flask, SQLite (SQL), REST API, Git. OOP throughout.
Run:  pip install -r requirements.txt && python app.py
Test: python test_api.py
"""
import json
import os
import sqlite3
from dataclasses import asdict, dataclass

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("DATABASE_PATH", "dsa.db")
SEED_PATH = os.path.join(os.path.dirname(__file__), "seed_problems.json")

app = Flask(__name__)


# --- Models (OOP) -------------------------------------------------------
@dataclass
class Problem:
    id: int
    slug: str
    title: str
    language: str
    file: str

    def to_dict(self):
        return asdict(self)


@dataclass
class LeaderboardEntry:
    team: str
    points: int
    college: str = ""

    def to_dict(self):
        return asdict(self)


# --- Database -----------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed the 42 real problems + leaderboard once."""
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS problems (
               id INTEGER PRIMARY KEY, slug TEXT NOT NULL,
               title TEXT NOT NULL, language TEXT NOT NULL, file TEXT NOT NULL,
               UNIQUE(slug, language))"""
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS leaderboard (
               id INTEGER PRIMARY KEY AUTOINCREMENT, team TEXT NOT NULL,
               points INTEGER NOT NULL, college TEXT NOT NULL DEFAULT '')"""
    )
    if db.execute("SELECT COUNT(*) FROM problems").fetchone()[0] == 0:
        with open(SEED_PATH, encoding="utf-8") as f:
            for p in json.load(f):
                db.execute(
                    "INSERT INTO problems (id, slug, title, language, file)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (p["id"], p["slug"], p["title"], p["language"], p["file"]),
                )
    if db.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0] == 0:
        # Real, verified live state of Hackathon Rivals (Season 2026):
        # 2 teams / 2 colleges, 1 leaderboard entry at 27 pts.
        db.execute(
            "INSERT INTO leaderboard (team, points, college)"
            " VALUES (?, ?, ?)",
            ("Hackathon", 27, ""),
        )
    db.commit()
    db.close()


class ProblemRepository:
    """All SQL lives here — the route handlers stay thin."""

    def __init__(self, db):
        self.db = db

    def list(self, query=None, language=None):
        sql = "SELECT * FROM problems WHERE 1=1"
        params = []
        if query:
            sql += " AND (title LIKE ? OR slug LIKE ?)"
            params += [f"%{query}%", f"%{query}%"]
        if language:
            sql += " AND language = ?"
            params.append(language)
        sql += " ORDER BY id"
        return [Problem(**dict(r)) for r in self.db.execute(sql, params)]

    def get(self, problem_id):
        row = self.db.execute(
            "SELECT * FROM problems WHERE id = ?", (problem_id,)
        ).fetchone()
        return Problem(**dict(row)) if row else None

    def create(self, problem):
        cur = self.db.execute(
            "INSERT INTO problems (slug, title, language, file)"
            " VALUES (?, ?, ?, ?)",
            (problem.slug, problem.title, problem.language, problem.file),
        )
        self.db.commit()
        return self.get(cur.lastrowid)


# --- Routes -------------------------------------------------------------
@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/stats")
def stats():
    db = get_db()
    rows = db.execute(
        "SELECT language, COUNT(*) AS n FROM problems GROUP BY language"
    ).fetchall()
    return jsonify(
        {
            "total_problems": db.execute(
                "SELECT COUNT(*) FROM problems"
            ).fetchone()[0],
            "by_language": {r["language"]: r["n"] for r in rows},
            "teams": 2,
            "colleges": 2,
        }
    )


@app.get("/api/problems")
def list_problems():
    repo = ProblemRepository(get_db())
    problems = repo.list(
        query=request.args.get("q"), language=request.args.get("language")
    )
    return jsonify([p.to_dict() for p in problems])


@app.get("/api/problems/<int:problem_id>")
def get_problem(problem_id):
    problem = ProblemRepository(get_db()).get(problem_id)
    if problem is None:
        return jsonify({"error": "problem not found"}), 404
    return jsonify(problem.to_dict())


@app.post("/api/problems")
def create_problem():
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("slug", "title", "language", "file") if not data.get(f)]
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400
    try:
        problem = ProblemRepository(get_db()).create(
            Problem(id=0, slug=data["slug"], title=data["title"],
                    language=data["language"], file=data["file"])
        )
    except sqlite3.IntegrityError:
        return jsonify({"error": "slug already exists"}), 409
    return jsonify(problem.to_dict()), 201


@app.get("/api/leaderboard")
def leaderboard():
    db = get_db()
    rows = db.execute(
        "SELECT team, points, college FROM leaderboard ORDER BY points DESC"
    ).fetchall()
    return jsonify([LeaderboardEntry(**dict(r)).to_dict() for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
