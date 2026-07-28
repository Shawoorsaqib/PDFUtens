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
from utils.converters import word_to_pdf as convert_word_to_pdf
from utils.cleanup import cleanup_old_files, delete_file_pair, delete_files

word_to_pdf_bp = Blueprint("word_to_pdf", __name__)


@word_to_pdf_bp.route("/word-to-pdf")
def word_to_pdf():
    """Renders the Word to PDF tool page."""
    return render_template("tools/word_to_pdf.html")


@word_to_pdf_bp.route("/word-to-pdf/upload", methods=["POST"])
def upload_word_to_pdf():
    """
    Handles Word file upload (.doc / .docx), converts it to PDF,
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
            "message": "No file uploaded. Please select a Word document."
        }), 400

    file = uploaded_files[0]
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".docx") or filename_lower.endswith(".doc")):
        return jsonify({
            "success": False,
            "message": "Unsupported file format. Please upload a Word document (.doc or .docx)."
        }), 400

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = convert_word_to_pdf(uploaded_path)

        # Delete uploaded input Word file since conversion is complete
        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/word-to-pdf/download/{output_filename}"
        })

    except Exception as e:
        delete_files([uploaded_path])
        return jsonify({
            "success": False,
            "message": f"Conversion failed: {str(e)}"
        }), 500


@word_to_pdf_bp.route("/word-to-pdf/download/<filename>")
def download_converted_pdf(filename):
    """
    Serves the converted PDF for download and cleans up the generated file.
    """
    output_folder = current_app.config.get("OUTPUT_FOLDER", "outputs")
    output_path = os.path.join(output_folder, filename)

    if not os.path.exists(output_path):
        return jsonify({
            "success": False,
            "message": "File not found or has already been downloaded."
        }), 404

    # Read output file into memory buffer to release file lock on disk before sending
    with open(output_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())

    # Delete output PDF file from disk after reading
    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
