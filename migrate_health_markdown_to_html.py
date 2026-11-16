"""
One-time migration: convert existing HealthArticle Markdown bodies to HTML.

Idempotent — skips articles that already look like HTML (contain '<' tags).

Local:
    python migrate_health_markdown_to_html.py

Railway:
    Called from start.sh → runs idempotently on every deploy.
    Skips already-converted articles.
"""
import re

from app import create_app
from app.extensions import db
from app.models.health import HealthArticle
import markdown as md


def looks_like_html(text):
    """True if text contains common HTML tags — means it's already converted."""
    if not text:
        return False
    return bool(re.search(r'<(p|h[1-6]|ul|ol|li|strong|em|blockquote)\b', text, re.IGNORECASE))


def convert_article(article):
    """Convert one article's body from Markdown → HTML, preserving its structure."""
    original = article.body or ""
    if looks_like_html(original):
        return False  # already HTML
    if not original.strip():
        return False  # empty

    html = md.markdown(original, extensions=["fenced_code", "tables", "nl2br"])
    article.body = html
    return True


def main():
    app = create_app()
    with app.app_context():
        articles = HealthArticle.query.all()
        converted = 0
        skipped = 0

        for a in articles:
            if convert_article(a):
                converted += 1
                print(f"[migrate] Converted article #{a.id}: {a.title}")
            else:
                skipped += 1

        if converted:
            db.session.commit()
            print(f"\n[migrate] Done. Converted {converted} article(s), skipped {skipped}.")
        else:
            print(f"[migrate] No articles needed conversion. {skipped} already HTML or empty.")


if __name__ == "__main__":
    main()