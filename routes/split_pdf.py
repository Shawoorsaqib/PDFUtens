from flask import Blueprint, render_template

split_pdf_bp = Blueprint("split_pdf", __name__)


@split_pdf_bp.route("/split-pdf")
def split_pdf():
    return render_template("tools/split_pdf.html")
