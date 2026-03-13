#!/usr/bin/env python3
"""Fetches RSS feeds from sources.json and stores articles in SQLite."""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

import feedparser
from dateutil import parser as dateparser

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "articles.db")
SOURCES_PATH = os.path.join(os.path.dirname(__file__), "sources.json")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT,
    published TEXT,
    summary TEXT,
    status TEXT DEFAULT 'new',
    created_at TEXT DEFAULT (datetime('now'))
);
"""


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        return " ".join(self.parts).strip()


def strip_html(html_text):
    if not html_text:
        return ""
    stripper = HTMLStripper()
    stripper.feed(html_text)
    text = stripper.get_text()
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def load_sources():
    with open(SOURCES_PATH) as f:
        data = json.load(f)
    return [s for s in data["sources"] if s.get("enabled", True)]


def url_hash(url):
    return hashlib.sha256(url.encode()).hexdigest()


def fetch_feed(source, cutoff_date):
    """Fetch a single feed and return list of article dicts."""
    articles = []
    feed = feedparser.parse(
        source["url"],
        agent="RSS-Learning-Digest/1.0 (personal learning tool)",
        request_headers={"Connection": "close"},
    )

    if feed.bozo and not feed.entries:
        raise Exception(f"Feed parse error: {feed.bozo_exception}")

    for entry in feed.entries:
        url = entry.get("link", "")
        if not url:
            continue

        title = entry.get("title", "No title")

        # Parse published date
        published = None
        for date_field in ("published", "updated", "created"):
            raw = entry.get(date_field)
            if raw:
                try:
                    published = dateparser.parse(raw)
                    break
                except (ValueError, TypeError):
                    continue

        # Skip articles older than cutoff
        if published:
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            if published < cutoff_date:
                continue

        # Get summary
        summary_raw = entry.get("summary", "") or entry.get("description", "")
        summary = strip_html(summary_raw)
        # Truncate very long summaries
        if len(summary) > 1000:
            summary = summary[:1000] + "..."

        articles.append(
            {
                "url_hash": url_hash(url),
                "url": url,
                "title": title,
                "source": source["name"],
                "category": source.get("category", ""),
                "published": published.isoformat() if published else None,
                "summary": summary,
            }
        )

    return articles


def main():
    parser = argparse.ArgumentParser(description="Collect RSS feed articles")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    args = parser.parse_args()

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    conn = init_db()
    sources = load_sources()

    total_added = 0
    total_dupes = 0
    feeds_fetched = 0

    for source in sources:
        try:
            articles = fetch_feed(source, cutoff_date)
            feeds_fetched += 1
            for article in articles:
                try:
                    conn.execute(
                        """INSERT INTO articles (url_hash, url, title, source, category, published, summary)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            article["url_hash"],
                            article["url"],
                            article["title"],
                            article["source"],
                            article["category"],
                            article["published"],
                            article["summary"],
                        ),
                    )
                    total_added += 1
                except sqlite3.IntegrityError:
                    total_dupes += 1
            conn.commit()
        except Exception as e:
            print(f"  [ERROR] {source['name']}: {e}", file=sys.stderr)

    conn.close()
    print(f"{feeds_fetched} feeds fetched, {total_added} articles added, {total_dupes} duplicates skipped")


if __name__ == "__main__":
    main()
