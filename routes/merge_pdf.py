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
from utils.pdf_utils import merge_pdfs
from utils.cleanup import cleanup_old_files, delete_files, delete_file_pair

merge_pdf_bp = Blueprint("merge_pdf", __name__)


@merge_pdf_bp.route("/merge-pdf")
def merge_pdf():
    """Renders the Merge PDF tool page."""
    return render_template("tools/merge_pdf.html")


@merge_pdf_bp.route("/merge-pdf/upload", methods=["POST"])
def merge_pdf_upload():
    """
    Handles uploaded PDF files, merges them, cleans up temporary files,
    and returns a JSON response with the download URL.
    """
    # Proactively clean up files older than 1 hour
    cleanup_old_files()

    files = request.files.getlist("file")
    if not files or all(f.filename == "" for f in files):
        files = request.files.getlist("files")

    valid_files = [f for f in files if f.filename != ""]

    if len(valid_files) < 2:
        return jsonify({
            "success": False,
            "message": "Please select at least two PDF files to merge."
        }), 400

    pdf_paths = []

    try:
        for file in valid_files:
            filename, path = save_uploaded_file(file)
            pdf_paths.append(path)

        output_filename, output_path = merge_pdfs(pdf_paths)

        # Clean up temporary uploaded files since they are merged
        delete_files(pdf_paths)

        return jsonify({
            "success": True,
            "download_url": f"/merge-pdf/download/{output_filename}",
            "filename": output_filename
        })

    except Exception as e:
        # Clean up any uploaded files if an error occurred
        if pdf_paths:
            delete_files(pdf_paths)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@merge_pdf_bp.route("/merge-pdf/download/<filename>")
def download_merged_pdf(filename):
    """
    Serves the merged PDF for download and cleans up the generated output file.
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