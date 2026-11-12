from flask import Blueprint, Response, request
from datetime import datetime
from app.models.health import HealthArticle

sitemap_bp = Blueprint("sitemap", __name__)


@sitemap_bp.route("/sitemap.xml")
def sitemap():
    base_url = request.url_root.rstrip("/")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # ── Static public pages ─────────────────────────────────
    pages = [
        {"loc": f"{base_url}/",              "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{base_url}/announcements", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base_url}/health",        "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base_url}/gallery",       "priority": "0.7", "changefreq": "weekly"},
    ]

    # ── Dynamic: published health articles ──────────────────
    try:
        articles = HealthArticle.query.filter_by(is_published=True).all()
        for a in articles:
            lastmod = a.updated_at or a.created_at or datetime.utcnow()
            pages.append({
                "loc": f"{base_url}/health/{a.slug}",
                "priority": "0.6",
                "changefreq": "monthly",
                "lastmod": lastmod.strftime("%Y-%m-%d"),
            })
    except Exception as e:
        # If DB query fails, still return the static sitemap
        print(f"[sitemap] Health articles query failed: {e}")

    # ── Build XML ───────────────────────────────────────────
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for page in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{page['loc']}</loc>")
        lines.append(f"    <lastmod>{page.get('lastmod', today)}</lastmod>")
        lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        lines.append(f"    <priority>{page['priority']}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")

    xml = "\n".join(lines)
    return Response(xml, mimetype="application/xml")


@sitemap_bp.route("/robots.txt")
def robots():
    base_url = request.url_root.rstrip("/")
    txt = f"""User-agent: *
Allow: /
Disallow: /auth/
Disallow: /dashboard/
Disallow: /members/
Disallow: /users/
Disallow: /ministries/
Disallow: /families/
Disallow: /content/
Disallow: /health/admin/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(txt, mimetype="text/plain")