from flask import Blueprint, render_template

pdf_to_word_bp = Blueprint("pdf_to_word", __name__)


@pdf_to_word_bp.route("/pdf-to-word")
def pdf_to_word():
    return render_template("tools/pdf_to_word.html")
