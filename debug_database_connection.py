#!/usr/bin/env python3
"""
验证数据库连接问题
"""

import os
import sqlite3
import sys

def check_database_connections():
    print("=== 数据库连接验证 ===")
    
    # 检查环境变量
    print("\n1. 当前环境变量:")
    db_path_env = os.getenv("DB_PATH")
    print(f"   DB_PATH环境变量: {db_path_env}")
    
    # 检查src/app/database.py中的DB_PATH
    print("\n2. 数据库模块中的DB_PATH:")
    try:
        # 模拟数据库模块的行为
        db_path_str = os.getenv("DB_PATH", "data/m33_lotto.db")
        print(f"   默认DB_PATH: {db_path_str}")
        
        # 检查文件是否存在
        if os.path.exists(db_path_str):
            print(f"   ✅ 数据库文件存在: {db_path_str}")
        else:
            print(f"   ❌ 数据库文件不存在: {db_path_str}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 检查实际数据库内容
    print("\n3. 检查各数据库内容:")
    
    databases = [
        ("Bot 1 (默认)", "data/m33_lotto.db"),
        ("Bot 2", "data/bot2.db"),
        ("环境变量指向", db_path_env if db_path_env else "未设置")
    ]
    
    for name, path in databases:
        if path and path != "未设置":
            print(f"\n   {name}: {path}")
            if os.path.exists(path):
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    
                    # 检查bet_items表
                    cursor.execute("SELECT COUNT(*) FROM bet_items WHERE status = 'accepted'")
                    bet_items_count = cursor.fetchone()[0]
                    
                    # 检查2026-04-07 MB的投注
                    cursor.execute('''
                        SELECT COUNT(*) 
                        FROM bet_items bi
                        JOIN bet_batches bb ON bi.batch_id = bb.id
                        WHERE bb.bet_date = '2026-04-07' 
                        AND bi.region_group = 'MB'
                        AND bi.status = 'accepted'
                        AND bb.status = 'accepted'
                    ''')
                    mb_2026_04_07_count = cursor.fetchone()[0]
                    
                    print(f"     总投注项: {bet_items_count}")
                    print(f"     2026-04-07 MB投注项: {mb_2026_04_07_count}")
                    
                    conn.close()
                except Exception as e:
                    print(f"     ❌ 数据库错误: {e}")
            else:
                print(f"     ❌ 数据库文件不存在")
    
    # 检查结算代码的实际行为
    print("\n4. 模拟结算代码行为:")
    
    # 模拟bet_selector.py的行为
    def simulate_bet_selector(draw_date, region_group):
        db_path_str = os.getenv("DB_PATH", "data/m33_lotto.db")
        print(f"   使用的数据库: {db_path_str}")
        
        if not os.path.exists(db_path_str):
            print(f"   ❌ 数据库不存在!")
            return []
        
        try:
            conn = sqlite3.connect(db_path_str)
            cursor = conn.cursor()
            
            # 执行与bet_selector.py相同的查询
            cursor.execute('''
                SELECT COUNT(*) 
                FROM bet_items bi
                INNER JOIN bet_batches bb ON bb.id = bi.batch_id
                WHERE bb.bet_date = ?
                  AND bi.region_group = ?
                  AND bi.status = 'accepted'
                  AND bb.status = 'accepted'
            ''', (draw_date, region_group))
            
            count = cursor.fetchone()[0]
            print(f"   找到 {count} 个投注项")
            
            conn.close()
            return count
        except Exception as e:
            print(f"   ❌ 查询错误: {e}")
            return 0
    
    print("\n   测试2026-04-07 MB结算查询:")
    count = simulate_bet_selector('2026-04-07', 'MB')
    
    if count == 0:
        print("   ⚠️ 问题: 结算代码找不到投注项!")
        print("   可能原因:")
        print("   1. 使用了错误的数据库")
        print("   2. 投注项状态不正确")
        print("   3. 查询条件有问题")

if __name__ == "__main__":
    check_database_connections()