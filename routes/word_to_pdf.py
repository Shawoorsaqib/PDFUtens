from flask import Blueprint, render_template

word_to_pdf_bp = Blueprint("word_to_pdf", __name__)


@word_to_pdf_bp.route("/word-to-pdf")
def word_to_pdf():
    return render_template("tools/word_to_pdf.html")
