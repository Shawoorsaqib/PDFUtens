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
from utils.pdf_utils import watermark_pdf_file
from utils.cleanup import cleanup_old_files, delete_file_pair, delete_files

watermark_pdf_bp = Blueprint("watermark_pdf", __name__)


@watermark_pdf_bp.route("/watermark-pdf")
def watermark_pdf():
    """Renders Watermark PDF tool page."""
    return render_template("tools/watermark_pdf.html")


@watermark_pdf_bp.route("/watermark-pdf/upload", methods=["POST"])
def upload_watermark_pdf():
    """
    Overlays text watermark onto PDF pages and returns download payload.
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

    text = request.form.get("text", "CONFIDENTIAL")
    opacity = request.form.get("opacity", "0.3")
    rotation = request.form.get("rotation", "45")

    uploaded_filename, uploaded_path = save_uploaded_file(file)

    try:
        output_filename, output_path = watermark_pdf_file(
            uploaded_path,
            watermark_text=text,
            opacity=opacity,
            rotation=rotation
        )

        delete_files([uploaded_path])

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/watermark-pdf/download/{output_filename}"
        })

    except Exception as e:
        delete_files([uploaded_path])
        return jsonify({
            "success": False,
            "message": f"Watermarking failed: {str(e)}"
        }), 500


@watermark_pdf_bp.route("/watermark-pdf/download/<filename>")
def download_watermarked_pdf(filename):
    """
    Serves watermarked PDF and cleans up file from disk.
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
