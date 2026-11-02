import re
from app.models.health import HealthArticle


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:200]


def unique_health_slug(title, exclude_id=None):
    base = slugify(title)
    if not base:
        base = "article"
    slug = base
    counter = 2
    while True:
        q = HealthArticle.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(HealthArticle.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base}-{counter}"
        counter += 1