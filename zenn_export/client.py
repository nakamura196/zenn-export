"""Zenn API client."""

import json
import time

import requests

API_BASE = "https://zenn.dev/api"


class ZennClient:
    """Client for the Zenn API."""

    def __init__(self, sleep_interval=0.3):
        self.sleep_interval = sleep_interval

    def _sleep(self):
        time.sleep(self.sleep_interval)

    def fetch_articles(self, username, count=100):
        """Fetch all articles for a user (handles pagination)."""
        articles = []
        page = 1
        while True:
            url = f"{API_BASE}/articles?username={username}&count={count}&order=latest&page={page}"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("articles", [])
            if not batch:
                break
            articles.extend(batch)
            next_page = data.get("next_page")
            if next_page is None:
                break
            page = next_page
            self._sleep()
        return articles

    def fetch_article_detail(self, slug):
        """Fetch article detail including body_html and topics."""
        url = f"{API_BASE}/articles/{slug}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json().get("article", {})

    def fetch_books(self, username):
        """Fetch all books for a user."""
        url = f"{API_BASE}/books?username={username}&count=100&order=latest"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json().get("books", [])

    def fetch_book_detail(self, slug):
        """Fetch book detail including chapters."""
        url = f"{API_BASE}/books/{slug}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json().get("book", {})

    def get_build_id(self):
        """Get Next.js build ID from Zenn."""
        resp = requests.get("https://zenn.dev/", timeout=10)
        idx = resp.text.find('__NEXT_DATA__')
        if idx < 0:
            return None
        tag_start = resp.text.find('>', idx) + 1
        tag_end = resp.text.find('</script>', tag_start)
        data = json.loads(resp.text[tag_start:tag_end])
        return data.get('buildId')

    def fetch_chapter_body(self, build_id, username, book_slug, chapter_slug):
        """Fetch chapter body HTML via _next/data endpoint."""
        url = f"https://zenn.dev/_next/data/{build_id}/{username}/books/{book_slug}/viewer/{chapter_slug}.json"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                pp = data.get("pageProps", {})
                chapters = pp.get("chapters", [])
                for ch in chapters:
                    if ch.get("slug") == chapter_slug:
                        body = ch.get("bodyHtml", ch.get("body_html", ""))
                        if body:
                            return body
                chapter = pp.get("chapter", {})
                if chapter:
                    return chapter.get("bodyHtml", chapter.get("body_html", ""))
        except Exception:
            pass
        return None
