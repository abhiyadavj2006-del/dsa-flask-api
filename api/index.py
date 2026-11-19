"""Vercel serverless entrypoint for the DSA Problems API.

Vercel's Python runtime turns files under api/ into serverless functions.
This module re-exports the Flask app from app.py so every route
(/health, /api/stats, /api/problems, /api/leaderboard) is served by it.

On Vercel the filesystem is read-only except /tmp, so the SQLite database
lives at /tmp/dsa.db (set via DATABASE_PATH in vercel.json). The app
re-seeds its 42 problems from seed_problems.json on every cold start.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DATABASE_PATH", "/tmp/dsa.db")

from app import app  # noqa: E402,F401  (re-exported for Vercel)
