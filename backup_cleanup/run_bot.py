#!/usr/bin/env python3
"""
简化版Bot启动脚本
解决Python导入路径问题
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("用法: python run_bot.py <bot编号>")
        print("示例: python run_bot.py 1")
        return 1
    
    bot_num = sys.argv[1]
    config_dir = Path(f"configs/bot_{bot_num}")
    
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