#!/usr/bin/env python3
"""
Debug当前系统状态
"""

import os
import sys
import sqlite3
from datetime import datetime

def check_database_status():
    """检查数据库状态"""
    print("=== 数据库状态检查 ===")
    
    databases = [
        ('Bot 1 (管理员)', 'data/m33_lotto.db'),
        ('Bot 2 (客户)', 'data/bot2.db')
    ]
    
    for name, path in databases:
        if os.path.exists(path):
            size = os.path.getsize(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            print(f"✅ {name}: {path}")
            print(f"   大小: {size:,} bytes, 修改时间: {mtime}")
            
            # 检查基本表结构
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"   表数量: {len(tables)}")
                conn.close()
            except Exception as e:
                print(f"   ❌ 数据库错误: {e}")
        else:
            print(f"❌ {name}: 数据库不存在 - {path}")

def check_config_status():
    """检查配置状态"""
    print("\n=== 配置状态检查 ===")
    
    # 检查主配置
    if os.path.exists('.env.multi'):
        print("✅ .env.multi 存在")
        with open('.env.multi', 'r') as f:
            lines = f.readlines()
            bot_count = sum(1 for line in lines if line.startswith('BOT_') and 'TOKEN=' in line and len(line.split('=')[1].strip()) > 10)
            print(f"   已配置bot数量: {bot_count}")
    else:
        print("❌ .env.multi 不存在")
    
    # 检查生成的配置
    config_dirs = ['configs/bot_1', 'configs/bot_2']
    for dir_path in config_dirs:
        if os.path.exists(dir_path):
            env_file = os.path.join(dir_path, '.env')
            if os.path.exists(env_file):
                print(f"✅ {dir_path}/.env 存在")
            else:
                print(f"❌ {dir_path}/.env 不存在")
        else:
            print(f"❌ {dir_path} 目录不存在")

def check_log_status():
    """检查日志状态"""
    print("\n=== 日志状态检查 ===")
    
    log_files = ['app.log']
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            print(f"✅ {log_file}: {size:,} bytes, 修改时间: {mtime}")
            
            # 检查最近错误
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-20:]  # 最后20行
                    errors = [l for l in lines if 'ERROR' in l or 'Conflict' in l]
                    if errors:
                        print(f"   ⚠️ 最近错误 ({len(errors)}个):")
                        for err in errors[-3:]:  # 显示最后3个错误
                            print(f"     {err.strip()}")
                    else:
                        print("   ✅ 最近无错误")
            except Exception as e:
                print(f"   ❌ 读取日志错误: {e}")
        else:
            print(f"❌ {log_file} 不存在")

def check_settlement_status():
    """检查结算状态"""
    print("\n=== 结算状态检查 ===")
    
    db_path = 'data/m33_lotto.db'
    if not os.path.exists(db_path):
        print("❌ 数据库不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查结算记录
        cursor.execute('''
            SELECT region_group, MAX(draw_date) as latest_date, COUNT(*) as count
            FROM settlement_runs 
            GROUP BY region_group
            ORDER BY region_group
        ''')
        settlements = cursor.fetchall()
        
        if settlements:
            print("结算记录:")
            for region, date, count in settlements:
                print(f"  {region}: 最新 {date}, 共{count}次结算")
        else:
            print("⚠️ 无结算记录")
        
        # 检查待结算的投注
        cursor.execute('''
            SELECT bb.bet_date, bb.region_group, COUNT(*) as bet_count
            FROM bet_batches bb
            LEFT JOIN settlement_runs sr ON bb.bet_date = sr.draw_date AND bb.region_group = sr.region_group
            WHERE bb.status = 'accepted'
            AND sr.id IS NULL  -- 未结算
            GROUP BY bb.bet_date, bb.region_group
            ORDER BY bb.bet_date DESC
            LIMIT 5
        ''')
        pending = cursor.fetchall()
        
        if pending:
            print("\n待结算投注:")
            for date, region, count in pending:
                print(f"  {date} {region}: {count}个投注")
        else:
            print("✅ 无待结算投注")
        
        conn.close()
    except Exception as e:
        print(f"❌ 检查结算状态错误: {e}")

def check_script_status():
    """检查脚本状态"""
    print("\n=== 脚本状态检查 ===")
    
    scripts = [
        ('setup_bots.py', '配置生成脚本'),
        ('run_bot.py', 'Bot启动脚本'),
        ('start_all_bots_simple.py', '批量启动脚本'),
        ('test_settlement.py', '结算测试脚本')
    ]
    
    for script, desc in scripts:
        if os.path.exists(script):
            print(f"✅ {script}: {desc}")
        else:
            print(f"❌ {script}: 不存在")

def main():
    print("🔍 M33 Lotto Bot 系统状态诊断")
    print("=" * 50)
    
    check_database_status()
    check_config_status()
    check_log_status()
    check_settlement_status()
    check_script_status()
    
    print("\n" + "=" * 50)
    print("诊断完成！")

if __name__ == "__main__":
    main()