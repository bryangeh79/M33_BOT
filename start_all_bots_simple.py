#!/usr/bin/env python3
"""
简单批量启动脚本 - 启动所有已配置的bot
"""

import os
import sys
import subprocess
import time
from pathlib import Path

from setup_bots import load_bot_configs, create_bot_config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def sync_all_bot_configs() -> None:
    """批量启动前，先把 .env.multi 同步到各 bot 配置目录。"""
    for bot_num, config in sorted(load_bot_configs().items()):
        if config.get("TOKEN"):
            create_bot_config(bot_num, config)

def get_configured_bots():
    """获取所有已配置的bot目录"""
    configs_dir = Path("configs")
    if not configs_dir.exists():
        return []
    
    bots = []
    for item in configs_dir.iterdir():
        if item.is_dir() and item.name.startswith("bot_"):
            try:
                bot_num = int(item.name.split("_")[1])
                # 检查是否有.env文件且包含有效的TOKEN
                env_file = item / ".env"
                if env_file.exists():
                    with open(env_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'BOT_TOKEN=' in content:
                            # 提取token值
                            for line in content.split('\n'):
                                if line.startswith('BOT_TOKEN='):
                                    token = line.split('=', 1)[1].strip()
                                    if token and token != 'YOUR_BOT_TOKEN_HERE':
                                        bots.append((bot_num, item))
                                        break
            except (ValueError, IndexError):
                continue
    
    return sorted(bots, key=lambda x: x[0])

def main():
    sync_all_bot_configs()
    print("🔍 扫描已配置的Bot...")
    bots = get_configured_bots()
    
    if not bots:
        print("❌ 没有找到已配置的Bot")
        print("请先运行: python setup_bots.py")
        return 1
    
    print(f"✅ 找到 {len(bots)} 个已配置的Bot:")
    for bot_num, bot_dir in bots:
        print(f"  Bot {bot_num}: {bot_dir}")
    
    print("\n🚀 开始启动所有Bot...")
    print("按 Ctrl+C 停止所有Bot")
    print("-" * 50)
    
    processes = []
    try:
        # 启动所有bot进程
        for bot_num, bot_dir in bots:
            print(f"启动 Bot {bot_num}...")
            
            cmd = [sys.executable, "src/app/main.py", "--config-dir", str(bot_dir)]
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd())
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            processes.append((bot_num, process))
            
            # 给每个bot一点启动时间
            time.sleep(2)
        
        print("\n✅ 所有Bot已启动!")
        print("正在运行中...")
        
        # 监控进程
        while True:
            all_alive = False
            for bot_num, process in processes:
                if process.poll() is None:
                    all_alive = True
                    # 读取输出
                    output = process.stdout.readline()
                    if output:
                        print(f"[Bot {bot_num}] {output}", end='')
                else:
                    print(f"❌ Bot {bot_num} 已退出，代码: {process.returncode}")
            
            if not all_alive:
                print("所有Bot都已停止")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在停止所有Bot...")
        
        # 停止所有进程
        for bot_num, process in processes:
            if process.poll() is None:
                process.terminate()
                print(f"正在停止 Bot {bot_num}...")
        
        # 等待进程结束
        for bot_num, process in processes:
            if process.poll() is None:
                process.wait(timeout=5)
                if process.poll() is None:
                    process.kill()
        
        print("✅ 所有Bot已停止")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
