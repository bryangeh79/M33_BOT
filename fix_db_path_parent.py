#!/usr/bin/env python3
"""
修复数据库路径的.parent调用问题
"""

import os
import re

files_to_fix = [
    "src/modules/admin/repositories/admin_user_repository.py",
    "src/modules/admin/repositories/agent_commission_repository.py",
    "src/modules/admin/repositories/bet_limit_repository.py",
    "src/modules/admin/repositories/bonus_payout_repository.py",
    "src/modules/admin/repositories/risk_control_repository.py",
    "src/modules/bet/repositories/daily_counter_repository.py",
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
    
    # 查找 self.db_path.parent 或 DB_PATH.parent 的调用
    patterns = [
        (r'self\.db_path\.parent\.mkdir', 'from pathlib import Path\n        Path(self.db_path).parent.mkdir'),
        (r'DB_PATH\.parent\.mkdir', 'from pathlib import Path\n    Path(DB_PATH).parent.mkdir'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            # 确保导入了Path
            if 'from pathlib import Path' not in content:
                # 在文件开头添加导入
                lines = content.split('\n')
                import_added = False
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        lines.insert(i, 'from pathlib import Path')
                        import_added = True
                        break
                if not import_added:
                    lines.insert(0, 'from pathlib import Path')
                content = '\n'.join(lines)
            
            # 替换调用
            if 'self.db_path.parent.mkdir' in pattern:
                content = re.sub(r'self\.db_path\.parent\.mkdir', 'Path(self.db_path).parent.mkdir', content)
                # 也需要修复sqlite3.connect调用
                content = re.sub(r'sqlite3\.connect\(self\.db_path\)', 'sqlite3.connect(str(self.db_path))', content)
            else:
                content = re.sub(r'DB_PATH\.parent\.mkdir', 'Path(DB_PATH).parent.mkdir', content)
                # 也需要修复sqlite3.connect调用
                content = re.sub(r'sqlite3\.connect\(DB_PATH\)', 'sqlite3.connect(str(DB_PATH))', content)
            
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
    print("修复数据库路径.parent调用问题...")
    fixed_count = 0
    
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n完成! 修复了 {fixed_count}/{len(files_to_fix)} 个文件")

if __name__ == "__main__":
    main()