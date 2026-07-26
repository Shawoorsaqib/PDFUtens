from flask import Blueprint, render_template

compress_pdf_bp = Blueprint("compress_pdf", __name__)


@compress_pdf_bp.route("/compress-pdf")
def compress_pdf():
    return render_template("tools/compress_pdf.html")
