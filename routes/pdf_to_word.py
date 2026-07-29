import io
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
from utils.converters import pdf_to_word as convert_pdf_to_word
from utils.cleanup import cleanup_old_files, delete_file_pair, delete_files
from utils.validators import safe_join_path

pdf_to_word_bp = Blueprint("pdf_to_word", __name__)


@pdf_to_word_bp.route("/pdf-to-word")
def pdf_to_word():
    """Renders the PDF to Word tool page."""
    return render_template("tools/pdf_to_word.html")


@pdf_to_word_bp.route("/pdf-to-word/upload", methods=["POST"])
def upload_pdf_to_word():
    """
    Handles PDF file upload, converts it to Word (.docx),
    and returns a JSON response with download URL.
    """
    # Proactively clean up files older than 1 hour
    cleanup_old_files()

    uploaded_files = request.files.getlist("file")
    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        uploaded_files = request.files.getlist("files")

    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        return jsonify({
            "success": False,
            "message": "No file uploaded. Please select a PDF file."
        }), 400

    file = uploaded_files[0]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "message": "Unsupported file format. Please upload a PDF file."
        }), 400

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = convert_pdf_to_word(uploaded_path)

        # Delete uploaded input PDF file since conversion is complete
        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/pdf-to-word/download/{output_filename}"
        })

    except Exception as e:
        delete_files([uploaded_path])
        return jsonify({
            "success": False,
            "message": f"Conversion failed: {str(e)}"
        }), 500


@pdf_to_word_bp.route("/pdf-to-word/download/<path:filename>")
@pdf_to_word_bp.route("/pdf-to-word/download/<filename>")
def download_word_file(filename):
    """
    Serves the converted Word (.docx) document for download and cleans up the generated file.
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

    # Read output file into memory buffer to release file lock on disk before sending
    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    # Delete output DOCX file from disk after reading
    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )