# File handling utilities
import os
import uuid

import config

from utils.validators import sanitize_filename


def generate_unique_filename(filename):
    """
    Generates a unique filename while preserving the extension.

    Example:
        image.png
    becomes:
        8f0d6c5b8d1240c49a0f0c2d9f1f5f8a.png
    """

    extension = os.path.splitext(filename)[1]

    unique_name = f"{uuid.uuid4().hex}{extension.lower()}"

    return unique_name


def save_uploaded_file(file):
    """
    Saves an uploaded file into the uploads folder.

    Returns:
        saved_filename
        saved_path
    """

    filename = sanitize_filename(file.filename)

    unique_filename = generate_unique_filename(filename)

    save_path = os.path.join(
        config.UPLOAD_FOLDER,
        unique_filename
    )

    file.save(save_path)

    return unique_filename, save_path