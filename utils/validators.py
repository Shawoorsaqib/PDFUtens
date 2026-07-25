# Validation utilities
from werkzeug.utils import secure_filename
import os

import config


def get_file_extension(filename):
    """
    Returns the file extension in lowercase.
    Example:
        image.PNG -> png
    """
    return os.path.splitext(filename)[1].lower().replace(".", "")


def is_allowed_image(filename):
    """
    Checks if the uploaded file is a supported image.
    """
    extension = get_file_extension(filename)
    return extension in config.ALLOWED_IMAGE_EXTENSIONS


def is_allowed_document(filename):
    """
    Checks if the uploaded file is a supported document.
    """
    extension = get_file_extension(filename)
    return extension in config.ALLOWED_DOCUMENT_EXTENSIONS


def sanitize_filename(filename):
    """
    Removes unsafe characters from filenames.
    """
    return secure_filename(filename)