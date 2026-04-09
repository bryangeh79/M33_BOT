import os
from pathlib import Path

# 确保DB_PATH始终是Path对象
db_path_str = os.getenv("DB_PATH", "data/m33_lotto.db")
DB_PATH = Path(db_path_str)
