import os
import shutil
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
        pass
    return getattr(config, key, None)


def _log_error(msg, exc=None):
    """
    Helper to log errors using current_app logger or fallback to print.
    """
    error_msg = f"{msg}: {exc}" if exc else msg
    try:
        if current_app:
            current_app.logger.error(error_msg)
            return
    except RuntimeError:
        pass
    print(error_msg)


def _safe_remove_file(file_path):
    """
    Safely removes a file, handling potential Windows file lock / permission errors gracefully.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            _log_error(f"Failed to remove file '{file_path}'", e)
            return False
    return False


def delete_file_pair(filename):
    """
    Deletes the generated output file and matching uploaded file(s) from UPLOAD_FOLDER and OUTPUT_FOLDER.
    Performs intelligent stem matching for single-file, merged, split, rotated, compressed, or converted outputs.
    """
    if not filename:
        return

    stem = os.path.splitext(os.path.basename(filename))[0]

    # 1. Delete generated file in OUTPUT_FOLDER
    output_folder = _get_folder("OUTPUT_FOLDER")
    if output_folder:
        out_path = os.path.join(output_folder, filename)
        _safe_remove_file(out_path)

    # 2. Delete matching uploaded original file(s) in UPLOAD_FOLDER
    upload_folder = _get_folder("UPLOAD_FOLDER")
    if upload_folder and os.path.exists(upload_folder):
        try:
            clean_stem = stem
            for prefix in ["merged_", "split_", "compressed_", "rotated_"]:
                if clean_stem.startswith(prefix):
                    clean_stem = clean_stem[len(prefix):]

            for fname in os.listdir(upload_folder):
                up_stem = os.path.splitext(fname)[0]
                if up_stem == stem or up_stem == clean_stem or up_stem in stem or clean_stem in up_stem:
                    uploaded_path = os.path.join(upload_folder, fname)
                    _safe_remove_file(uploaded_path)
        except Exception as e:
            _log_error(f"Failed to delete uploaded files matching stem '{stem}'", e)


def cleanup_old_files(max_age_seconds=3600):
    """
    Scans upload, output, and temp folders to delete files and directories older than max_age_seconds.
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
                    try:
                        file_age = now - os.path.getmtime(fpath)
                        if file_age > max_age_seconds:
                            if os.path.isdir(fpath):
                                shutil.rmtree(fpath, ignore_errors=True)
                            else:
                                _safe_remove_file(fpath)
                    except Exception as e:
                        _log_error(f"Failed to check/remove stale item '{fpath}'", e)
            except Exception as e:
                _log_error(f"Error scanning folder '{folder}' for stale files", e)


def delete_files(file_paths):
    """
    Deletes multiple files safely.
    """
    if not file_paths:
        return

    for path in file_paths:
        _safe_remove_file(path)