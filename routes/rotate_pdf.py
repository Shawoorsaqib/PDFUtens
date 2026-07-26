from flask import Blueprint, render_template

rotate_pdf_bp = Blueprint("rotate_pdf", __name__)


@rotate_pdf_bp.route("/rotate-pdf")
def rotate_pdf():
    return render_template("tools/rotate_pdf.html")
