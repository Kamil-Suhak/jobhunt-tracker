import os
from pathlib import Path

APP_DIR_NAME = ".jobhunt-tracker"
DB_FILE_NAME = "tracker.db"


def get_app_dir() -> Path:
    app_dir = Path.home() / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_db_path() -> Path:
    override = os.environ.get("JHT_DB_PATH")
    if override:
        path = Path(override)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return get_app_dir() / DB_FILE_NAME
