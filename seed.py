import sqlite3
from pathlib import Path

import requests

from crawler import MAX_ITEMS, RSS_URL, fetch_news

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "posts.db"


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )


def seed_posts() -> int:
    articles = fetch_news(RSS_URL, MAX_ITEMS)
    added_count = 0

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)

        for article in articles:
            title = article["title"].strip()
            exists = conn.execute(
                "SELECT 1 FROM posts WHERE title = ? LIMIT 1", (title,)
            ).fetchone()
            if exists:
                continue

            content = (
                f"{article['summary']}\n\n"
                f"링크: {article['link']}\n"
                f"발행시간: {article['pub_date']}"
            )
            conn.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)",
                (title, content),
            )
            added_count += 1

    return added_count


if __name__ == "__main__":
    try:
        inserted = seed_posts()
        print(f"{inserted}건 추가됨")
    except requests.RequestException as e:
        print(f"RSS 요청 중 오류가 발생했습니다: {e}")
