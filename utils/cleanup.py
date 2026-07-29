import os
import shutil
import time
from flask import current_app
from werkzeug.utils import secure_filename
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


def _is_within_allowed_directory(file_path):
    """
    Verifies that file_path strictly resides within UPLOAD_FOLDER, OUTPUT_FOLDER, or TEMP_FOLDER,
    and is NOT equal to the folder root itself.
    """
    if not file_path or not isinstance(file_path, str):
        return False

    allowed_folders = [
        _get_folder("UPLOAD_FOLDER"),
        _get_folder("OUTPUT_FOLDER"),
        _get_folder("TEMP_FOLDER")
    ]

    try:
        target_abs = os.path.realpath(os.path.abspath(file_path))
    except Exception:
        return False

    for folder in allowed_folders:
        if not folder:
            continue
        try:
            folder_abs = os.path.realpath(os.path.abspath(folder))
            # Must be strictly inside folder_abs (starts with folder_abs + os.sep) and NOT equal to folder_abs
            if target_abs.startswith(folder_abs + os.sep) and target_abs != folder_abs:
                return True
        except Exception:
            continue

    return False


def _safe_remove_file(file_path):
    """
    Safely removes a file or directory, validating canonical path boundaries
    and handling potential Windows file lock / permission errors gracefully.
    """
    if not _is_within_allowed_directory(file_path):
        _log_error(f"Security Alert: Blocked unauthorized file removal outside target directories: '{file_path}'")
        return False

    if os.path.exists(file_path):
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)
            else:
                os.remove(file_path)
            return True
        except Exception as e:
            _log_error(f"Failed to remove item '{file_path}'", e)
            return False
    return False


def delete_file_pair(filename):
    """
    Deletes the generated output file and matching uploaded file(s) from UPLOAD_FOLDER and OUTPUT_FOLDER.
    Sanitizes untrusted filename inputs to prevent path traversal during file cleanup.
    """
    if not filename or not isinstance(filename, str):
        return

    # Extract clean basename to sanitize input
    clean_filename = secure_filename(os.path.basename(filename))
    if not clean_filename or clean_filename in (".", ".."):
        return

    stem = os.path.splitext(clean_filename)[0]

    # 1. Delete generated file in OUTPUT_FOLDER
    output_folder = _get_folder("OUTPUT_FOLDER")
    if output_folder and os.path.exists(output_folder):
        out_path = os.path.join(output_folder, clean_filename)
        _safe_remove_file(out_path)

        # Also search for any output files matching stem
        try:
            for fname in os.listdir(output_folder):
                if fname == ".gitkeep":
                    continue
                if fname == clean_filename or os.path.splitext(fname)[0] == stem:
                    _safe_remove_file(os.path.join(output_folder, fname))
        except Exception as e:
            _log_error(f"Failed scanning output folder for stem '{stem}'", e)

    # 2. Delete matching uploaded original file(s) in UPLOAD_FOLDER
    upload_folder = _get_folder("UPLOAD_FOLDER")
    if upload_folder and os.path.exists(upload_folder):
        try:
            clean_stem = stem
            for prefix in ["merged_", "split_", "compressed_", "rotated_", "protected_", "unlocked_", "watermarked_", "cleaned_"]:
                if clean_stem.startswith(prefix):
                    clean_stem = clean_stem[len(prefix):]

            for fname in os.listdir(upload_folder):
                if fname == ".gitkeep":
                    continue
                up_stem = os.path.splitext(fname)[0]
                if up_stem == stem or up_stem == clean_stem or up_stem in stem or clean_stem in up_stem:
                    uploaded_path = os.path.join(upload_folder, fname)
                    _safe_remove_file(uploaded_path)
        except Exception as e:
            _log_error(f"Failed to delete uploaded files matching stem '{stem}'", e)


def cleanup_old_files(max_age_seconds=300):
    """
    Scans upload, output, and temp folders to delete files and directories older than max_age_seconds.
    Preserves .gitkeep placeholders.
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
                    if fname == ".gitkeep":
                        continue
                    fpath = os.path.join(folder, fname)
                    try:
                        file_age = now - os.path.getmtime(fpath)
                        if file_age > max_age_seconds:
                            _safe_remove_file(fpath)
                    except Exception as e:
                        _log_error(f"Failed to check/remove stale item '{fpath}'", e)
            except Exception as e:
                _log_error(f"Error scanning folder '{folder}' for stale files", e)


def purge_all_outputs():
    """
    Completely purges all files and directories in upload, output, and temp folders (excluding .gitkeep).
    """
    folders = [
        _get_folder("UPLOAD_FOLDER"),
        _get_folder("OUTPUT_FOLDER"),
        _get_folder("TEMP_FOLDER")
    ]

    for folder in folders:
        if folder and os.path.exists(folder):
            try:
                for fname in os.listdir(folder):
                    if fname == ".gitkeep":
                        continue
                    fpath = os.path.join(folder, fname)
                    _safe_remove_file(fpath)
            except Exception as e:
                _log_error(f"Error purging folder '{folder}'", e)


def delete_files(file_paths):
    """
    Deletes multiple files safely.
    """
    if not file_paths:
        return

    for path in file_paths:
        _safe_remove_file(path)