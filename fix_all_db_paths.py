#!/usr/bin/env python3
"""
修复所有数据库路径转换问题
"""

import os
import re

files_to_fix = [
    "src/modules/admin/repositories/admin_user_repository.py",
    "src/modules/admin/repositories/agent_commission_repository.py",
    "src/modules/admin/repositories/bet_limit_repository.py",
    "src/modules/admin/repositories/bonus_payout_repository.py",
    "src/modules/admin/repositories/risk_control_repository.py",
    "src/modules/customer/repositories/agent_customer_repository.py",
    "src/modules/customer/repositories/user_preference_repository.py",
    "src/modules/report/repositories/report_repository.py",
    "src/modules/settlement/repositories/settlement_repository.py",
]

def fix_file(filepath):
    """修复单个文件"""
    if not os.path.exists(filepath):
        print(f"⚠ 文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # 修复1: 确保DB_PATH被转换为Path
    if 'self.db_path = Path(db_path) if db_path else DB_PATH' in content:
        content = content.replace(
            'self.db_path = Path(db_path) if db_path else DB_PATH',
            'self.db_path = Path(db_path) if db_path else Path(DB_PATH)'
        )
        modified = True
    
    # 修复2: 确保sqlite3.connect使用字符串
    if 'sqlite3.connect(self.db_path)' in content and 'str(self.db_path)' not in content:
        content = content.replace(
            'sqlite3.connect(self.db_path)',
            'sqlite3.connect(str(self.db_path))'
        )
        modified = True
    
    # 修复3: 确保DB_PATH在connect调用中被转换为字符串
    if 'sqlite3.connect(DB_PATH)' in content and 'str(DB_PATH)' not in content:
        content = content.replace(
            'sqlite3.connect(DB_PATH)',
            'sqlite3.connect(str(DB_PATH))'
        )
        modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复完成: {filepath}")
        return True
    else:
        print(f"⚠ 无需修复: {filepath}")
        return False

def main():
    print("修复所有数据库路径转换问题...")
    fixed_count = 0
    
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n完成! 修复了 {fixed_count}/{len(files_to_fix)} 个文件")

if __name__ == "__main__":
    main()