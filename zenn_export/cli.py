"""CLI entry point for zenn-export."""

import argparse
import sys

from .exporter import export_articles, export_books


def main():
    parser = argparse.ArgumentParser(
        prog="zenn-export",
        description="Export Zenn articles and books as Markdown files.",
    )
    parser.add_argument("username", help="Zenn username")
    parser.add_argument("-o", "--output", default="./output", help="Output directory (default: ./output)")
    parser.add_argument("--articles-only", action="store_true", help="Export articles only")
    parser.add_argument("--books-only", action="store_true", help="Export books only")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    args = parser.parse_args()

    do_articles = not args.books_only
    do_books = not args.articles_only

    try:
        if do_articles:
            export_articles(args.username, args.output, force=args.force)
        if do_books:
            export_books(args.username, args.output, force=args.force)
        print("\nAll done!")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
