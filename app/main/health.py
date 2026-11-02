from flask import Blueprint, render_template, abort
from app.models.health import HealthArticle

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health_list():
    articles = (
        HealthArticle.query
        .filter_by(is_published=True)
        .order_by(HealthArticle.published_at.desc())
        .all()
    )
    return render_template("public/health.html", articles=articles)


@health_bp.route("/health/<slug>")
def health_detail(slug):
    article = HealthArticle.query.filter_by(slug=slug, is_published=True).first()
    if not article:
        abort(404)
    return render_template("public/health_article.html", article=article)