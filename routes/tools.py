import io
from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app
)

import os
import shutil

from utils.validators import (
    is_allowed_image,
    is_allowed_document
)
from utils.file_handler import save_uploaded_file
from utils.converters import image_to_pdf
from utils.cleanup import delete_file_pair, cleanup_old_files

tools_bp = Blueprint("tools", __name__)


@tools_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Uploads a file after validation and converts it to PDF.
    Also cleans up any stale/abandoned files.
    """
    # Proactively clean up files older than 1 hour
    cleanup_old_files(max_age_seconds=3600)

    # Check if a file was sent
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file uploaded."
        }), 400

    file = request.files["file"]

    # Check empty filename
    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    # Validate file type
    if not (
        is_allowed_image(file.filename)
        or
        is_allowed_document(file.filename)
    ):
        return jsonify({
            "success": False,
            "message": "Unsupported file type."
        }), 400

    # Save uploaded file
    filename, path = save_uploaded_file(file)

    # Convert image to PDF or handle document file
    pdf_filename = None

    if is_allowed_image(filename):
        pdf_filename, _ = image_to_pdf(path)
    else:
        pdf_filename = filename
        if not pdf_filename.lower().endswith(".pdf"):
            pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
        output_path = os.path.join(current_app.config["OUTPUT_FOLDER"], pdf_filename)
        shutil.copy(path, output_path)

    return jsonify({
        "success": True,
        "uploaded_file": filename,
        "pdf_file": pdf_filename,
        "download_url": f"/download/{pdf_filename}" if pdf_filename else None
    })


@tools_bp.route("/download/<filename>")
def download_file(filename):
    """
    Serves the converted file for download, then deletes both the 
    generated PDF and the uploaded original file immediately.
    """
    output_folder = current_app.config["OUTPUT_FOLDER"]
    output_path = os.path.join(output_folder, filename)

    if not os.path.exists(output_path):
        return jsonify({
            "success": False,
            "message": "File not found or has already been downloaded."
        }), 404

    # Read output file into memory buffer to release file lock on disk
    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    # Delete both the uploaded image and generated PDF from disk
    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
