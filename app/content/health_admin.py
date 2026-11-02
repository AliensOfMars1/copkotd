from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.auth.decorators import role_required
from app.utils.roles import Role
from app.models.health import HealthArticle
from app.utils.cloudinary import upload_image, delete_image
from app.utils.slug import unique_health_slug

health_admin_bp = Blueprint("health_admin", __name__, url_prefix="/health/admin")

ALLOWED_ROLES = (Role.SUPER_ADMIN, Role.HEALTH_OFFICER)

CATEGORIES = [
    "Nutrition",
    "Mental Health",
    "Fitness",
    "Disease Prevention",
    "General Wellness",
    "Others",
]


@health_admin_bp.route("/")
@login_required
@role_required(*ALLOWED_ROLES)
def list_articles():
    articles = HealthArticle.query.order_by(HealthArticle.created_at.desc()).all()
    return render_template("content/health_list.html", articles=articles)


@health_admin_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def create_article():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        body = request.form.get("body", "").strip()
        category = request.form.get("category", "").strip()
        author_name = request.form.get("author_name", "").strip()
        is_published = request.form.get("is_published") == "on"

        if not title or not body:
            flash("Title and body are required.", "danger")
            return render_template("content/health_form.html", article=None, categories=CATEGORIES)

        slug = unique_health_slug(title)

        cover_url = None
        cover_pid = None
        cover_file = request.files.get("cover_image")
        if cover_file and cover_file.filename:
            try:
                result = upload_image(cover_file, folder="kotd/health")
                cover_url = result["url"]
                cover_pid = result["public_id"]
            except Exception as e:
                flash(f"Image upload failed: {e}", "warning")

        article = HealthArticle(
            title=title,
            slug=slug,
            summary=summary,
            body=body,
            category=category,
            author_name=author_name or (current_user.full_name if current_user else ""),
            cover_image_url=cover_url,
            cover_public_id=cover_pid,
            is_published=is_published,
            published_at=datetime.utcnow() if is_published else None,
            created_by=current_user.id,
        )
        db.session.add(article)
        db.session.commit()
        flash("Article created.", "success")
        return redirect(url_for("health_admin.list_articles"))

    return render_template("content/health_form.html", article=None, categories=CATEGORIES)


@health_admin_bp.route("/<int:article_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def edit_article(article_id):
    article = HealthArticle.query.get_or_404(article_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        body = request.form.get("body", "").strip()
        category = request.form.get("category", "").strip()
        author_name = request.form.get("author_name", "").strip()
        is_published = request.form.get("is_published") == "on"

        if not title or not body:
            flash("Title and body are required.", "danger")
            return render_template("content/health_form.html", article=article, categories=CATEGORIES)

        # Regenerate slug if title changed
        if title != article.title:
            article.slug = unique_health_slug(title, exclude_id=article.id)
        article.title = title
        article.summary = summary
        article.body = body
        article.category = category
        article.author_name = author_name

        # Handle new cover
        cover_file = request.files.get("cover_image")
        if cover_file and cover_file.filename:
            if article.cover_public_id:
                try:
                    delete_image(article.cover_public_id)
                except Exception:
                    pass
            try:
                result = upload_image(cover_file, folder="kotd/health")
                article.cover_image_url = result["url"]
                article.cover_public_id = result["public_id"]
            except Exception as e:
                flash(f"Image upload failed: {e}", "warning")

        # Handle publish/unpublish
        if is_published and not article.is_published:
            article.published_at = datetime.utcnow()
        article.is_published = is_published

        db.session.commit()
        flash("Article updated.", "success")
        return redirect(url_for("health_admin.list_articles"))

    return render_template("content/health_form.html", article=article, categories=CATEGORIES)


@health_admin_bp.route("/<int:article_id>/delete", methods=["POST"])
@login_required
@role_required(*ALLOWED_ROLES)
def delete_article(article_id):
    article = HealthArticle.query.get_or_404(article_id)
    if article.cover_public_id:
        try:
            delete_image(article.cover_public_id)
        except Exception:
            pass
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted.", "info")
    return redirect(url_for("health_admin.list_articles"))