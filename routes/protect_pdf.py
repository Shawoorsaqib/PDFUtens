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
from utils.pdf_utils import protect_pdf_file
from utils.cleanup import cleanup_old_files, delete_file_pair, delete_files
from utils.validators import safe_join_path

protect_pdf_bp = Blueprint("protect_pdf", __name__)


@protect_pdf_bp.route("/protect-pdf")
def protect_pdf():
    """Renders Protect PDF tool page."""
    return render_template("tools/protect_pdf.html")


@protect_pdf_bp.route("/protect-pdf/upload", methods=["POST"])
def upload_protect_pdf():
    """
    Encrypts uploaded PDF with password and returns download payload.
    """
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
            "message": "Invalid file format. Only PDF files are supported."
        }), 400

    password = request.form.get("password")
    if not password:
        return jsonify({
            "success": False,
            "message": "Please enter a password to protect your PDF."
        }), 400

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = protect_pdf_file(uploaded_path, password=password)

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/protect-pdf/download/{output_filename}"
        })

    except Exception as e:
        delete_files([uploaded_path])
        return jsonify({
            "success": False,
            "message": f"Protection failed: {str(e)}"
        }), 500


@protect_pdf_bp.route("/protect-pdf/download/<path:filename>")
@protect_pdf_bp.route("/protect-pdf/download/<filename>")
def download_protected_pdf(filename):
    """
    Serves encrypted PDF and cleans up file from disk.
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

    delete_file_pair(filename)

    return send_file(
        file_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
