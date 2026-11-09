"""Tests for the DSA Problems API — run with: python test_api.py"""
import os
import tempfile
import unittest

import app as api


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        api.DB_PATH = self.db_path
        api.init_db()
        api.app.config["TESTING"] = True
        self.client = api.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_health(self):
        self.assertEqual(self.client.get("/health").get_json(), {"status": "ok"})

    def test_stats_counts_all_42_problems(self):
        data = self.client.get("/api/stats").get_json()
        self.assertEqual(data["total_problems"], 42)
        self.assertEqual(data["by_language"], {"C": 24, "C++": 15, "Python": 3})

    def test_search_multiword(self):
        data = self.client.get("/api/problems?q=linked+list").get_json()
        self.assertTrue(all("linked" in p["slug"] or "linked" in p["title"].lower()
                            for p in data))
        self.assertGreaterEqual(len(data), 2)  # C and C++ linked-list problems

    def test_filter_by_language(self):
        data = self.client.get("/api/problems?language=Python").get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["slug"], "palindrome-check")

    def test_get_one_and_404(self):
        self.assertEqual(self.client.get("/api/problems/27").get_json()["slug"],
                         "two-sum")
        self.assertEqual(self.client.get("/api/problems/999").status_code, 404)

    def test_create_validates_and_rejects_duplicate(self):
        payload = {"slug": "binary-search", "title": "Binary Search",
                   "language": "Python", "file": "binary-search.py"}
        r = self.client.post("/api/problems", json=payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.post("/api/problems", json=payload).status_code,
                         409)
        self.assertEqual(
            self.client.post("/api/problems", json={"slug": "x"}).status_code, 400)

    def test_leaderboard(self):
        data = self.client.get("/api/leaderboard").get_json()
        self.assertEqual(data, [{"team": "Hackathon", "points": 27, "college": ""}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
