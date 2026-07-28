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
from utils.pdf_utils import rotate_pdf_file
from utils.cleanup import cleanup_old_files, delete_file_pair, delete_files

rotate_pdf_bp = Blueprint("rotate_pdf", __name__)


@rotate_pdf_bp.route("/rotate-pdf")
def rotate_pdf():
    """Renders the Rotate PDF tool page."""
    return render_template("tools/rotate_pdf.html")


@rotate_pdf_bp.route("/rotate-pdf/upload", methods=["POST"])
def upload_rotate_pdf():
    """
    Handles PDF file upload and page rotation.
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
            "message": "Invalid file type. Only PDF files are supported."
        }), 400

    angle = request.form.get("angle", 90)

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = rotate_pdf_file(uploaded_path, rotation_angle=angle)

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/rotate-pdf/download/{output_filename}"
        })

    except Exception as e:
        delete_files([uploaded_path])
        return jsonify({
            "success": False,
            "message": f"Rotation failed: {str(e)}"
        }), 500


@rotate_pdf_bp.route("/rotate-pdf/download/<filename>")
def download_rotated_pdf(filename):
    """
    Serves rotated PDF and deletes file after sending.
    """
    output_folder = current_app.config.get("OUTPUT_FOLDER", "outputs")
    output_path = os.path.join(output_folder, filename)

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
        download_name=filename
    )
