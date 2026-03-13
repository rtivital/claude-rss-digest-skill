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
    source_type TEXT DEFAULT 'article',
    full_content_rss INTEGER DEFAULT 0,
    published TEXT,
    summary TEXT,
    status TEXT DEFAULT 'new',
    created_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_FEED_HEALTH_SQL = """
CREATE TABLE IF NOT EXISTS feed_health (
    name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    consecutive_failures INTEGER DEFAULT 0,
    last_error TEXT,
    last_success TEXT,
    auto_disabled INTEGER DEFAULT 0
);
"""

AUTO_DISABLE_THRESHOLD = 3


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
    conn.execute(CREATE_FEED_HEALTH_SQL)
    # Migrate existing databases: add new columns if missing
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(articles)").fetchall()}
    if "source_type" not in existing_cols:
        conn.execute("ALTER TABLE articles ADD COLUMN source_type TEXT DEFAULT 'article'")
    if "full_content_rss" not in existing_cols:
        conn.execute("ALTER TABLE articles ADD COLUMN full_content_rss INTEGER DEFAULT 0")
    conn.commit()
    return conn


def load_sources():
    with open(SOURCES_PATH) as f:
        data = json.load(f)
    return [s for s in data["sources"] if s.get("enabled", True)]


def url_hash(url):
    return hashlib.sha256(url.encode()).hexdigest()


def is_feed_auto_disabled(conn, source_name):
    """Check if a feed has been auto-disabled due to repeated failures."""
    row = conn.execute(
        "SELECT auto_disabled FROM feed_health WHERE name = ?", (source_name,)
    ).fetchone()
    return row and row[0] == 1


def record_feed_success(conn, source):
    """Record a successful feed fetch, resetting failure count."""
    conn.execute(
        """INSERT INTO feed_health (name, url, consecutive_failures, last_success, auto_disabled)
           VALUES (?, ?, 0, datetime('now'), 0)
           ON CONFLICT(name) DO UPDATE SET
               consecutive_failures = 0,
               last_error = NULL,
               last_success = datetime('now'),
               auto_disabled = 0""",
        (source["name"], source["url"]),
    )


def record_feed_failure(conn, source, error_msg):
    """Record a feed failure and auto-disable if threshold exceeded."""
    conn.execute(
        """INSERT INTO feed_health (name, url, consecutive_failures, last_error)
           VALUES (?, ?, 1, ?)
           ON CONFLICT(name) DO UPDATE SET
               consecutive_failures = consecutive_failures + 1,
               last_error = ?""",
        (source["name"], source["url"], error_msg, error_msg),
    )
    row = conn.execute(
        "SELECT consecutive_failures FROM feed_health WHERE name = ?",
        (source["name"],),
    ).fetchone()
    if row and row[0] >= AUTO_DISABLE_THRESHOLD:
        conn.execute(
            "UPDATE feed_health SET auto_disabled = 1 WHERE name = ?",
            (source["name"],),
        )
        print(
            f"  [AUTO-DISABLED] {source['name']}: {row[0]} consecutive failures",
            file=sys.stderr,
        )


def get_summary_limit(source):
    """Newsletter sources get a higher summary truncation limit."""
    if source.get("type") == "newsletter":
        return 2000
    return 1000


def fetch_feed(source, cutoff_date):
    """Fetch a single feed and return list of article dicts."""
    articles = []
    summary_limit = get_summary_limit(source)
    source_type = source.get("type", "article")
    full_content = 1 if source.get("full_content_rss", False) else 0

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
        # Truncate based on source type
        if len(summary) > summary_limit:
            summary = summary[:summary_limit] + "..."

        articles.append(
            {
                "url_hash": url_hash(url),
                "url": url,
                "title": title,
                "source": source["name"],
                "category": source.get("category", ""),
                "source_type": source_type,
                "full_content_rss": full_content,
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
    feeds_skipped = 0

    for source in sources:
        if is_feed_auto_disabled(conn, source["name"]):
            print(f"  [SKIPPED] {source['name']}: auto-disabled due to repeated failures", file=sys.stderr)
            feeds_skipped += 1
            continue

        try:
            articles = fetch_feed(source, cutoff_date)
            feeds_fetched += 1
            record_feed_success(conn, source)
            for article in articles:
                try:
                    conn.execute(
                        """INSERT INTO articles (url_hash, url, title, source, category, source_type, full_content_rss, published, summary)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            article["url_hash"],
                            article["url"],
                            article["title"],
                            article["source"],
                            article["category"],
                            article["source_type"],
                            article["full_content_rss"],
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
            record_feed_failure(conn, source, str(e))
            conn.commit()

    conn.close()
    msg = f"{feeds_fetched} feeds fetched, {total_added} articles added, {total_dupes} duplicates skipped"
    if feeds_skipped:
        msg += f", {feeds_skipped} feeds auto-disabled"
    print(msg)


if __name__ == "__main__":
    main()
