import os
import time
from flask import current_app
import config


def _get_folder(key):
    """
    Safely retrieves a folder path from current_app config or fallback to config module.
    """
    try:
        if current_app:
            folder = current_app.config.get(key)
            if folder:
                return folder
    except RuntimeError:
        # Occurs when called outside of Flask application context
        pass
    return getattr(config, key, None)


def delete_file_pair(pdf_filename):
    """
    Deletes the generated output PDF and its corresponding uploaded file(s).
    Matching is performed by comparing the unique filename stem.
    """
    if not pdf_filename:
        return

    stem = os.path.splitext(pdf_filename)[0]

    # 1. Delete generated PDF in OUTPUT_FOLDER
    output_folder = _get_folder("OUTPUT_FOLDER")
    if output_folder:
        pdf_path = os.path.join(output_folder, pdf_filename)
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception as e:
                try:
                    current_app.logger.error(f"Failed to delete output PDF '{pdf_path}': {e}")
                except RuntimeError:
                    print(f"Failed to delete output PDF '{pdf_path}': {e}")

    # 2. Delete matching uploaded original file in UPLOAD_FOLDER
    upload_folder = _get_folder("UPLOAD_FOLDER")
    if upload_folder and os.path.exists(upload_folder):
        try:
            for fname in os.listdir(upload_folder):
                if os.path.splitext(fname)[0] == stem:
                    uploaded_path = os.path.join(upload_folder, fname)
                    if os.path.exists(uploaded_path):
                        os.remove(uploaded_path)
        except Exception as e:
            try:
                current_app.logger.error(f"Failed to delete uploaded file for stem '{stem}': {e}")
            except RuntimeError:
                print(f"Failed to delete uploaded file for stem '{stem}': {e}")


def cleanup_old_files(max_age_seconds=3600):
    """
    Scans upload, output, and temp folders to delete files older than max_age_seconds.
    Defaults to 1 hour (3600 seconds) to remove abandoned files.
    """
    now = time.time()
    folders = [
        _get_folder("UPLOAD_FOLDER"),
        _get_folder("OUTPUT_FOLDER"),
        _get_folder("TEMP_FOLDER")
    ]

    for folder in folders:
        if folder and os.path.exists(folder):
            try:
                for fname in os.listdir(folder):
                    fpath = os.path.join(folder, fname)
                    if os.path.isfile(fpath):
                        file_age = now - os.path.getmtime(fpath)
                        if file_age > max_age_seconds:
                            try:
                                os.remove(fpath)
                            except Exception as e:
                                try:
                                    current_app.logger.error(f"Failed to remove stale file '{fpath}': {e}")
                                except RuntimeError:
                                    print(f"Failed to remove stale file '{fpath}': {e}")
            except Exception as e:
                try:
                    current_app.logger.error(f"Error scanning folder '{folder}' for stale files: {e}")
                except RuntimeError:
                    print(f"Error scanning folder '{folder}' for stale files: {e}")
