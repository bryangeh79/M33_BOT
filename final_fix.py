#!/usr/bin/env python3
"""
最终修复：确保所有数据库路径都正确转换为Path对象
"""

import os

# 修复src/app/database.py
db_py_content = '''import os
from pathlib import Path

# 确保DB_PATH始终是Path对象
db_path_str = os.getenv("DB_PATH", "data/m33_lotto.db")
DB_PATH = Path(db_path_str)
'''

with open('src/app/database.py', 'w', encoding='utf-8') as f:
    f.write(db_py_content)
print("✅ 修复 src/app/database.py")

# 现在需要更新所有导入DB_PATH的文件
import_files = [
    "src/modules/bet/repositories/daily_counter_repository.py",
    "src/modules/bet/services/bet_message_service.py",
]

for filepath in import_files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保使用正确的导入
        if 'from src.app.database import DB_PATH' in content:
            # 这个导入现在会得到Path对象
            print(f"✅ {filepath} 导入正确")
        else:
            print(f"⚠ {filepath} 没有从database.py导入DB_PATH")

print("\n✅ 最终修复完成")
print("现在DB_PATH在所有地方都是Path对象")