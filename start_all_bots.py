#!/usr/bin/env python3
"""
批量启动所有已配置的Bot
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import threading

def get_configured_bots():
    """获取所有已配置的bot编号"""
    env_file = Path(".env.multi")
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        return []
    
    bots = set()
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _ = line.split('=', 1)
                key = key.strip()
                
                # 检查是否是bot配置
                if key.startswith('BOT_') and '_TOKEN' in key:
                    # 提取bot编号: BOT_1_TOKEN -> 1
                    try:
                        bot_num = int(key.split('_')[1])
                        bots.add(bot_num)
                    except (IndexError, ValueError):
                        continue
    
    return sorted(bots)

def start_bot(bot_number):
    """启动单个bot（线程函数）"""
    print(f"🚀 启动Bot {bot_number}...")
    
    try:
        # 使用start_bot.py来启动
        cmd = [sys.executable, "start_bot.py", str(bot_number)]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in process.stdout:
            print(f"[Bot {bot_number}] {line}", end='')
        
        process.wait()
        if process.returncode == 0:
            print(f"✅ Bot {bot_number} 已正常停止")
        else:
            print(f"❌ Bot {bot_number} 异常退出，代码: {process.returncode}")
            
    except Exception as e:
        print(f"❌ 启动Bot {bot_number} 失败: {e}")

def main():
    print("🔍 扫描已配置的Bot...")
    bots = get_configured_bots()
    
    if not bots:
        print("❌ 没有找到已配置的Bot")
        print("请在 .env.multi 文件中配置至少一个Bot")
        return 1
    
    print(f"✅ 找到 {len(bots)} 个已配置的Bot: {bots}")
    
    # 检查哪些bot有配置token
    active_bots = []
    for bot_num in bots:
        env_file = Path(".env.multi")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"BOT_{bot_num}_TOKEN="):
                    token = line.split('=', 1)[1].strip()
                    if token:
                        active_bots.append(bot_num)
                    break
    
    if not active_bots:
        print("❌ 没有找到已配置TOKEN的Bot")
        print("请在 .env.multi 文件中为Bot配置TOKEN")
        return 1
    
    print(f"🚀 准备启动 {len(active_bots)} 个Bot: {active_bots}")
    print("按 Ctrl+C 停止所有Bot")
    print("-" * 50)
    
    threads = []
    try:
        # 启动所有bot线程
        for bot_num in active_bots:
            thread = threading.Thread(target=start_bot, args=(bot_num,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(1)  # 稍微延迟，避免同时启动冲突
        
        # 等待所有线程
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在停止所有Bot...")
        # 这里可以添加更优雅的停止逻辑
        print("✅ 所有Bot已停止")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())