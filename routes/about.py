from flask import Blueprint, render_template

about_bp = Blueprint("about", __name__)


@about_bp.route("/about")
def about():
    """Renders the About Us page."""
    return render_template("about.html")


@about_bp.route("/privacy")
def privacy():
    """Renders the Privacy Policy page."""
    return render_template("privacy.html")


@about_bp.route("/terms")
def terms():
    """Renders the Terms & Conditions page."""
    return render_template("terms.html")
