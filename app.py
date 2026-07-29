import os
import time
from flask import Flask, render_template

import config
from routes import register_routes
from utils.cleanup import purge_all_outputs, cleanup_old_files

app = Flask(__name__)

# Configure application
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = config.OUTPUT_FOLDER
app.config["TEMP_FOLDER"] = config.TEMP_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.secret_key = config.SECRET_KEY

# Ensure directories exist and purge stale files from previous sessions
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)
with app.app_context():
    purge_all_outputs()

# Track last cleanup timestamp for request throttling
_last_cleanup_time = 0.0


@app.before_request
def periodic_cleanup():
    global _last_cleanup_time
    now = time.time()
    # Run cleanup at most once every 30 seconds
    if now - _last_cleanup_time > 30.0:
        _last_cleanup_time = now
        cleanup_old_files(max_age_seconds=300)


# Register route blueprints
register_routes(app)


@app.route("/")
def home():
    """Renders the landing page."""
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)