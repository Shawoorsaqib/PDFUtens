import os

# Base Directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Upload Folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")

# Maximum Upload Size (100 MB)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

# Secret Key
SECRET_KEY = "replace-this-with-a-random-secret-key"

# Allowed Extensions
ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "tiff",
    "webp"
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "txt"
}