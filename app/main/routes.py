from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # For now, render your existing homepage.
    # Later this will pull from Homepage_Content.
    return render_template("public/index.html")