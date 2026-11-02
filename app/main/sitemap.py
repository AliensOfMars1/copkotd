from flask import Blueprint, Response
from datetime import datetime

sitemap_bp = Blueprint("sitemap", __name__)


@sitemap_bp.route("/sitemap.xml")
def sitemap():
    # Domain — Flask will auto-build absolute URLs based on request
    from flask import request
    base_url = request.url_root.rstrip("/")

    # Static pages with priority and change frequency
    pages = [
        {"loc": f"{base_url}/", "priority": "1.0", "changefreq": "weekly"},
        # Future: add /about, /sermons/archive, etc. when they exist
    ]

    today = datetime.utcnow().strftime("%Y-%m-%d")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    for page in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{page['loc']}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        lines.append(f"    <priority>{page['priority']}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")

    xml = "\n".join(lines)
    return Response(xml, mimetype="application/xml")

@sitemap_bp.route("/robots.txt")
def robots():
    from flask import request
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

Sitemap: {base_url}/sitemap.xml
"""
    return Response(txt, mimetype="text/plain")