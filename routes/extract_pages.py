import io
import json
import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app

from utils.file_handler import save_uploaded_file
from utils.pdf_utils import extract_pages as extract_pages_util
from utils.cleanup import cleanup_old_files, delete_files, delete_file_pair
from utils.validators import is_allowed_document

extract_pages_bp = Blueprint("extract_pages", __name__)


@extract_pages_bp.route("/extract-pages")
def extract_pages():
    """Renders the Extract Pages tool page."""
    return render_template("tools/extract_pages.html")


@extract_pages_bp.route("/extract-pages/upload", methods=["POST"])
def extract_pages_upload():
    """
    Handles PDF upload, extracts specified page numbers/ranges into a new PDF,
    cleans up temporary files, and returns JSON response with download URL.
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

    pages_to_extract_raw = request.form.get("pages", request.form.get("pages_to_extract"))
    if not pages_to_extract_raw:
        return jsonify({"success": False, "message": "Please specify page numbers to extract."}), 400

    try:
        pages_to_extract = json.loads(pages_to_extract_raw)
    except Exception:
        pages_to_extract = pages_to_extract_raw

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = extract_pages_util(
            pdf_path=uploaded_path,
            pages_to_extract=pages_to_extract
        )

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "download_url": f"/extract-pages/download/{output_filename}",
            "filename": output_filename
        })

    except Exception as e:
        if os.path.exists(uploaded_path):
            delete_files([uploaded_path])

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400 if isinstance(e, ValueError) else 500


@extract_pages_bp.route("/extract-pages/download/<filename>")
def download_extract_pages(filename):
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
