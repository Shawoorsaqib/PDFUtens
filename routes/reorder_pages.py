import io
import json
import os
from flask import Blueprint, render_template, request, jsonify, send_file, current_app

from utils.file_handler import save_uploaded_file
from utils.pdf_utils import reorder_pages as reorder_pages_util
from utils.cleanup import cleanup_old_files, delete_files, delete_file_pair
from utils.validators import is_allowed_document, safe_join_path

reorder_pages_bp = Blueprint("reorder_pages", __name__)


@reorder_pages_bp.route("/reorder-pages")
def reorder_pages():
    """Renders the Reorder Pages tool page."""
    return render_template("tools/reorder_pages.html")


@reorder_pages_bp.route("/reorder-pages/upload", methods=["POST"])
def reorder_pages_upload():
    """
    Handles PDF upload, reorders pages according to specified sequence,
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

    page_order_raw = request.form.get("order", request.form.get("page_order"))
    if not page_order_raw:
        return jsonify({"success": False, "message": "Please specify page order sequence."}), 400

    try:
        page_order = json.loads(page_order_raw)
    except Exception:
        page_order = page_order_raw

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = reorder_pages_util(
            pdf_path=uploaded_path,
            page_order=page_order
        )

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "download_url": f"/reorder-pages/download/{output_filename}",
            "filename": output_filename
        })

    except Exception as e:
        if os.path.exists(uploaded_path):
            delete_files([uploaded_path])

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400 if isinstance(e, ValueError) else 500


@reorder_pages_bp.route("/reorder-pages/download/<path:filename>")
@reorder_pages_bp.route("/reorder-pages/download/<filename>")
def download_reorder_pages(filename):
    """
    Serves the output PDF file for download and cleans up.
    """
    output_folder = current_app.config.get("OUTPUT_FOLDER", "outputs")
    try:
        output_path = safe_join_path(output_folder, filename)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid download request or file path."}), 400

    if not os.path.exists(output_path):
        return jsonify({"success": False, "message": "File not found or has already been downloaded."}), 404

    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
