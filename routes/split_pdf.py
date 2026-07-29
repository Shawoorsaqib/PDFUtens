import io
import json
import os
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    current_app
)

from utils.file_handler import save_uploaded_file
from utils.pdf_utils import split_pdf as split_pdf_util
from utils.cleanup import cleanup_old_files, delete_files, delete_file_pair
from utils.validators import is_allowed_document, safe_join_path

split_pdf_bp = Blueprint("split_pdf", __name__)


@split_pdf_bp.route("/split-pdf")
def split_pdf():
    """Renders the Split PDF tool page."""
    return render_template("tools/split_pdf.html")


@split_pdf_bp.route("/split-pdf/upload", methods=["POST"])
def split_pdf_upload():
    """
    Handles PDF upload, splits pages according to chosen mode/ranges,
    cleans up temporary uploaded files, and returns JSON response with download URL.
    """
    cleanup_old_files()

    file = request.files.get("file")
    if not file or file.filename == "":
        files = request.files.getlist("files")
        if files and files[0].filename != "":
            file = files[0]

    if not file or file.filename == "":
        return jsonify({
            "success": False,
            "message": "No PDF file provided."
        }), 400

    if not is_allowed_document(file.filename) or not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "message": "Only PDF files are supported for splitting."
        }), 400

    split_mode = request.form.get("split_mode", request.form.get("splitMode", "all"))
    ranges_raw = request.form.get("ranges")

    ranges = None
    if split_mode == "range" and ranges_raw:
        try:
            ranges = json.loads(ranges_raw)
        except Exception:
            ranges = None

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = split_pdf_util(
            pdf_path=uploaded_path,
            split_mode=split_mode,
            ranges=ranges
        )

        # Cleanup original uploaded PDF file
        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "download_url": f"/split-pdf/download/{output_filename}",
            "filename": output_filename
        })

    except Exception as e:
        if os.path.exists(uploaded_path):
            delete_files([uploaded_path])

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400 if isinstance(e, ValueError) else 500


@split_pdf_bp.route("/split-pdf/download/<path:filename>")
@split_pdf_bp.route("/split-pdf/download/<filename>")
def download_split_pdf(filename):
    """
    Serves the split output file (.pdf or .zip) for download and cleans up.
    """
    output_folder = current_app.config.get("OUTPUT_FOLDER", "outputs")
    try:
        output_path = safe_join_path(output_folder, filename)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid download request or file path."
        }), 400

    if not os.path.exists(output_path):
        return jsonify({
            "success": False,
            "message": "File not found or has already been downloaded."
        }), 404

    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    # Delete output file from disk after reading
    delete_file_pair(filename)

    mimetype = "application/zip" if filename.lower().endswith(".zip") else "application/pdf"

    return send_file(
        file_bytes,
        mimetype=mimetype,
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
