# Validation & Security utilities
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
    if not filename:
        return ""
    return secure_filename(os.path.basename(filename))


def safe_join_path(base_folder, filename):
    """
    Safely joins a base folder with a user-supplied filename.
    Enforces strict path traversal prevention:
    1. Rejects empty, null, or traversal token filenames.
    2. Rejects filenames containing path separators ('/', '\\') or '..' tokens.
    3. Sanitizes the filename using secure_filename.
    4. Verifies that the canonical absolute realpath resides strictly inside base_folder.

    Returns:
        str: Verified absolute file path within base_folder.
    Raises:
        ValueError: If path traversal or invalid filename is detected.
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Invalid or missing filename.")

    # Reject any filename containing path separators or directory traversal sequences
    if ".." in filename or "/" in filename or "\\" in filename or "%" in filename:
        raise ValueError("Path traversal attempt detected.")

    clean_basename = secure_filename(filename)
    if not clean_basename or clean_basename != filename or clean_basename in (".", ".."):
        raise ValueError("Unsafe filename after sanitization.")

    base_abs = os.path.realpath(os.path.abspath(base_folder))
    target_abs = os.path.realpath(os.path.abspath(os.path.join(base_abs, clean_basename)))

    # Ensure target_abs is strictly inside base_abs directory boundary
    if not (target_abs.startswith(base_abs + os.sep) or target_abs == base_abs):
        raise ValueError("Path traversal attempt detected.")

    return target_abs