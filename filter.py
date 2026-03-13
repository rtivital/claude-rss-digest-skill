#!/usr/bin/env python3
"""Keyword pre-filter to reduce articles before sending to Claude."""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "articles.db")
TOPICS_PATH = os.path.join(os.path.dirname(__file__), "topics.json")


def load_keywords():
    with open(TOPICS_PATH) as f:
        data = json.load(f)

    topics = data["profile"]["topics"]

    def extract(items):
        """Split comma-separated keyword phrases into individual keywords."""
        keywords = []
        for item in items:
            for part in item.split(","):
                kw = part.strip().strip("()")
                if kw:
                    keywords.append(kw.lower())
        return keywords

    return extract(topics["high_priority"]), extract(topics["medium_priority"])


def score_article(title, summary, high_keywords, medium_keywords):
    text = (title + " " + (summary or "")).lower()
    score = 0
    for kw in high_keywords:
        if kw in text:
            score += 3
    for kw in medium_keywords:
        if kw in text:
            score += 1
    return score


def main():
    high_kw, medium_kw = load_keywords()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, title, summary FROM articles WHERE status = 'new'").fetchall()

    kept = 0
    filtered = 0

    for row in rows:
        s = score_article(row["title"], row["summary"], high_kw, medium_kw)
        if s >= 3:
            kept += 1
        else:
            conn.execute("UPDATE articles SET status = 'filtered' WHERE id = ?", (row["id"],))
            filtered += 1

    conn.commit()
    conn.close()
    print(f"{kept} articles kept, {filtered} filtered out")


if __name__ == "__main__":
    main()
