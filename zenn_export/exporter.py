"""Export Zenn articles and books as Markdown files."""

import json
import os

from .client import ZennClient
from .converter import html_to_markdown


def export_articles(username, output_dir, force=False, client=None):
    """Export all articles for a user as Markdown files.

    Returns the number of articles exported.
    """
    client = client or ZennClient()
    os.makedirs(output_dir, exist_ok=True)

    print("Fetching article list...")
    articles = client.fetch_articles(username)
    total = len(articles)
    print(f"Found {total} articles")

    exported = 0
    for i, article in enumerate(articles):
        slug = article["slug"]
        title = article["title"]
        md_path = os.path.join(output_dir, f"{slug}.md")

        if not force and os.path.exists(md_path):
            print(f"[{i+1}/{total}] Skipping (exists): {title[:50]}")
            continue

        print(f"[{i+1}/{total}] Downloading: {title[:50]}...")
        try:
            detail = client.fetch_article_detail(slug)
            body_html = detail.get("body_html", "")
            body_md = html_to_markdown(body_html)

            topics = [t.get("name", "") for t in detail.get("topics", [])]
            published = article.get("published_at", "")
            emoji = article.get("emoji", "")

            frontmatter = (
                f'---\n'
                f'title: "{title}"\n'
                f'emoji: "{emoji}"\n'
                f'type: "tech"\n'
                f'topics: {json.dumps(topics, ensure_ascii=False)}\n'
                f'published: true\n'
                f'published_at: "{published}"\n'
                f'source: "https://zenn.dev/{username}/articles/{slug}"\n'
                f'---\n\n'
            )

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(frontmatter + body_md)

            exported += 1
            client._sleep()
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n{exported} articles saved to {output_dir}")
    return exported


def export_books(username, output_dir, force=False, client=None):
    """Export all books for a user as Markdown files.

    Returns the number of books exported.
    """
    client = client or ZennClient()
    os.makedirs(output_dir, exist_ok=True)

    print("\nFetching book list...")
    books = client.fetch_books(username)
    total = len(books)
    print(f"Found {total} books")

    build_id = client.get_build_id()
    print(f"Build ID: {build_id}")

    exported = 0
    for i, book in enumerate(books):
        book_slug = book["slug"]
        book_title = book["title"]
        print(f"\n[Book {i+1}/{total}] {book_title}")

        book_dir = os.path.join(output_dir, book_slug)
        os.makedirs(book_dir, exist_ok=True)

        try:
            detail = client.fetch_book_detail(book_slug)
        except Exception as e:
            print(f"  Error fetching book detail: {e}")
            continue

        topics = [t.get("name", "") for t in detail.get("topics", [])]
        chapters = detail.get("chapters", [])
        summary = detail.get("summary", "")
        published_at = detail.get("published_at", book.get("published_at", ""))
        cover = detail.get("cover_image_url", "")

        # Save book config
        config_path = os.path.join(book_dir, "config.md")
        if force or not os.path.exists(config_path):
            chapter_list = "\n".join(
                f'  - slug: "{ch.get("slug", "")}"\n    title: "{ch.get("title", "")}"'
                for ch in chapters
            )
            config_content = (
                f'---\n'
                f'title: "{book_title}"\n'
                f'topics: {json.dumps(topics, ensure_ascii=False)}\n'
                f'published: true\n'
                f'published_at: "{published_at}"\n'
                f'cover: "{cover}"\n'
                f'source: "https://zenn.dev/{username}/books/{book_slug}"\n'
                f'chapters:\n'
                f'{chapter_list}\n'
                f'---\n\n'
                f'{summary}\n'
            )
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)

        # Download chapters
        for j, ch in enumerate(chapters):
            ch_slug = ch.get("slug", "")
            ch_title = ch.get("title", "")
            ch_path = os.path.join(book_dir, f"{ch_slug}.md")

            if not force and os.path.exists(ch_path):
                print(f"  Chapter {j+1}/{len(chapters)}: Skipping (exists)")
                continue

            print(f"  Chapter {j+1}/{len(chapters)}: {ch_title[:40]}...")

            body_html = None
            if build_id:
                body_html = client.fetch_chapter_body(build_id, username, book_slug, ch_slug)

            if body_html:
                body_md = html_to_markdown(body_html)
            else:
                body_md = "(本文はZennサイトでご覧ください)"

            ch_content = (
                f'---\n'
                f'title: "{ch_title}"\n'
                f'book: "{book_title}"\n'
                f'position: {ch.get("position", j+1)}\n'
                f'source: "https://zenn.dev/{username}/books/{book_slug}/viewer/{ch_slug}"\n'
                f'---\n\n'
                f'{body_md}\n'
            )
            with open(ch_path, "w", encoding="utf-8") as f:
                f.write(ch_content)

            client._sleep()

        exported += 1

    print(f"\n{exported} books saved to {output_dir}")
    return exported
