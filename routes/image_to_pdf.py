import io
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    current_app
)

import os
import shutil

from utils.validators import (
    is_allowed_image,
    is_allowed_document,
    safe_join_path
)
from utils.file_handler import save_uploaded_file
from utils.converters import image_to_pdf as convert_image_to_pdf, images_to_pdf
from utils.cleanup import delete_file_pair, cleanup_old_files

image_to_pdf_bp = Blueprint("image_to_pdf", __name__)


@image_to_pdf_bp.route("/image-to-pdf")
def image_to_pdf():
    """Renders the Image to PDF tool page."""
    return render_template("tools/image_to_pdf.html")


@image_to_pdf_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Uploads file(s) after validation and converts image(s) to PDF.
    Also cleans up any stale/abandoned files.
    """
    # Proactively clean up files older than 1 hour
    cleanup_old_files(max_age_seconds=3600)

    uploaded_files = request.files.getlist("file")
    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        uploaded_files = request.files.getlist("files")

    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        return jsonify({
            "success": False,
            "message": "No file uploaded."
        }), 400

    uploaded_files = [f for f in uploaded_files if f.filename != ""]

    saved_paths = []
    saved_filenames = []
    image_paths = []

    for file in uploaded_files:
        if not (
            is_allowed_image(file.filename)
            or
            is_allowed_document(file.filename)
        ):
            return jsonify({
                "success": False,
                "message": f"Unsupported file type: {file.filename}"
            }), 400

        filename, path = save_uploaded_file(file)
        saved_filenames.append(filename)
        saved_paths.append(path)
        if is_allowed_image(file.filename):
            image_paths.append(path)

    pdf_filename = None

    if image_paths:
        pdf_filename, _ = images_to_pdf(image_paths)
    elif saved_paths:
        filename = saved_filenames[0]
        path = saved_paths[0]
        pdf_filename = filename
        if not pdf_filename.lower().endswith(".pdf"):
            pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
        output_path = os.path.join(current_app.config["OUTPUT_FOLDER"], pdf_filename)
        shutil.copy(path, output_path)

    return jsonify({
        "success": True,
        "uploaded_files": saved_filenames,
        "pdf_file": pdf_filename,
        "download_url": f"/download/{pdf_filename}" if pdf_filename else None
    })


@image_to_pdf_bp.route("/download/<path:filename>")
@image_to_pdf_bp.route("/download/<filename>")
def download_file(filename):
    """
    Serves the converted file for download, then deletes both the 
    generated PDF and the uploaded original file immediately.
    """
    output_folder = current_app.config["OUTPUT_FOLDER"]
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

    # Read output file into memory buffer to release file lock on disk
    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    # Delete both the uploaded image and generated PDF from disk
    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
