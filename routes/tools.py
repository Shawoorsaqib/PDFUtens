from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    current_app
)

from utils.validators import (
    is_allowed_image,
    is_allowed_document
)

from utils.file_handler import save_uploaded_file
from utils.converters import image_to_pdf

tools_bp = Blueprint("tools", __name__)


@tools_bp.route("/upload", methods=["POST"])
def upload_file():
    """
    Uploads a file after validation.
    """

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

    # Convert image to PDF
    pdf_filename = None

    if is_allowed_image(filename):
        pdf_filename, _ = image_to_pdf(path)

    return jsonify({

        "success": True,

        "uploaded_file": filename,

        "pdf_file": pdf_filename,

        "download_url": (
            f"/download/{pdf_filename}"
            if pdf_filename
            else None
        )

    })


@tools_bp.route("/download/<filename>")
def download_file(filename):
    """
    Downloads the generated PDF.
    """

    return send_from_directory(
        current_app.config["OUTPUT_FOLDER"],
        filename,
        as_attachment=True
    )