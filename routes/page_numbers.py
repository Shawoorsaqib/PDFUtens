import io
import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app

from utils.file_handler import save_uploaded_file
from utils.pdf_utils import add_page_numbers as add_page_numbers_util
from utils.cleanup import cleanup_old_files, delete_files, delete_file_pair
from utils.validators import is_allowed_document

page_numbers_bp = Blueprint("page_numbers", __name__)


@page_numbers_bp.route("/add-page-numbers")
def page_numbers():
    """Renders the Add Page Numbers tool page."""
    return render_template("tools/page_numbers.html")


@page_numbers_bp.route("/add-page-numbers/upload", methods=["POST"])
def page_numbers_upload():
    """
    Handles PDF upload, adds customizable page numbers,
    cleans up temporary uploaded files, and returns JSON response with download URL.
    """
    cleanup_old_files()

    file = request.files.get("file")
    if not file or file.filename == "":
        files = request.files.getlist("files")
        if files and files[0].filename != "":
            file = files[0]

    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No PDF file provided."}), 400

    if not is_allowed_document(file.filename) or not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "Only PDF files are supported."}), 400

    position = request.form.get("position", "bottom-right")
    format_str = request.form.get("format", "Page {page} of {total}")
    start_page = request.form.get("start_page", 1)
    font_size = request.form.get("font_size", 10)

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = add_page_numbers_util(
            pdf_path=uploaded_path,
            position=position,
            format_str=format_str,
            start_page=start_page,
            font_size=font_size
        )

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "download_url": f"/add-page-numbers/download/{output_filename}",
            "filename": output_filename
        })

    except Exception as e:
        if os.path.exists(uploaded_path):
            delete_files([uploaded_path])

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400 if isinstance(e, ValueError) else 500


@page_numbers_bp.route("/add-page-numbers/download/<filename>")
def download_page_numbers(filename):
    """
    Serves the output PDF file for download and cleans up.
    """
    output_folder = current_app.config.get("OUTPUT_FOLDER", "outputs")
    output_path = os.path.join(output_folder, filename)

    if not os.path.exists(output_path):
        return jsonify({"success": False, "message": "File not found or has already been downloaded."}), 404

    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
