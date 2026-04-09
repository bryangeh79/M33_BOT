import os
from pathlib import Path

DEFAULT_DB_PATH = "data/m33_lotto.db"


def get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", DEFAULT_DB_PATH))


# Backward-compatible alias for older imports.
DB_PATH = get_db_path()
