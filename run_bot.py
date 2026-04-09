#!/usr/bin/env python3
"""
简化版Bot启动脚本
解决Python导入路径问题
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

from setup_bots import (
    DEFAULT_ENV_FILE,
    DEFAULT_OUTPUT_DIR,
    create_bot_config,
    load_bot_configs,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def sync_bot_config(bot_num: int, env_file: str | Path, output_dir: str | Path) -> Path | None:
    """启动前用 .env.multi 覆盖生成目标 bot 配置，避免旧 token 残留。"""
    bots = load_bot_configs(env_file)
    config = bots.get(bot_num)
    if not config:
        return None
    if not config.get("TOKEN"):
        return None
    return create_bot_config(bot_num, config, output_dir=output_dir)

def main():
    if len(sys.argv) < 2:
        print("用法: python run_bot.py <bot编号> [--env-file PATH] [--config-root PATH]")
        print("示例: python run_bot.py 1")
        return 1

    parser = argparse.ArgumentParser(description="启动单个 bot")
    parser.add_argument("bot_num")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="指定 .env.multi 路径")
    parser.add_argument("--config-root", default=str(DEFAULT_OUTPUT_DIR), help="指定 bot 配置目录根路径")
    args = parser.parse_args()

    bot_num_raw = args.bot_num
    if not bot_num_raw.isdigit():
        print(f"❌ 无效的bot编号: {bot_num_raw}")
        return 1

    bot_num = int(bot_num_raw)
    config_root = Path(args.config_root)
    synced_config_dir = sync_bot_config(bot_num, args.env_file, config_root)
    config_dir = synced_config_dir or config_root / f"bot_{bot_num}"
    
    if not config_dir.exists():
        print(f"❌ 配置目录不存在: {config_dir}")
        return 1
    
    # 检查.env文件
    env_file = config_dir / ".env"
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        return 1
    
    print(f"🚀 启动Bot {bot_num}...")
    print(f"   配置目录: {config_dir}")
    
    # 设置Python路径
    project_root = Path.cwd()
    python_path = str(project_root)
    
    if 'PYTHONPATH' in os.environ:
        python_path = os.environ['PYTHONPATH'] + os.pathsep + python_path
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = python_path
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    # 读取.env文件并设置环境变量
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip()
    
    # 运行主程序
    main_script = project_root / "src" / "app" / "main.py"
    
    cmd = [
        sys.executable,
        str(main_script),
        "--config-dir",
        str(config_dir)
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot {bot_num} 启动失败: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Bot {bot_num} 已停止")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
