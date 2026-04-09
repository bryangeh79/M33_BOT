#!/usr/bin/env python3
"""
多Bot启动脚本
用法: python start_bot.py <bot编号>
示例: python start_bot.py 1   # 启动Bot 1
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def load_bot_config(bot_number):
    """加载指定编号的bot配置"""
    env_file = Path(".env.multi")
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        return None
    
    config = {}
    prefix = f"BOT_{bot_number}_"
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 读取通用配置
                if not key.startswith('BOT_'):
                    config[key] = value
                # 读取指定bot的配置
                elif key.startswith(prefix):
                    config_key = key[len(prefix):]  # 去掉前缀
                    config[config_key] = value
    
    # 检查必要配置
    required_keys = ['TOKEN', 'DB_PATH', 'CLIENT_NAME', 'TIMEZONE']
    for req in required_keys:
        if req not in config:
            print(f"❌ Bot {bot_number} 缺少必要配置: {req}")
            return None
    
    if not config['TOKEN']:
        print(f"❌ Bot {bot_number} 的TOKEN未配置")
        return None
    
    return config

def create_env_file(config, bot_number):
    """创建临时的.env文件供bot使用"""
    env_content = f"""# Bot {bot_number} 配置
BOT_TOKEN={config['TOKEN']}
DB_PATH={config['DB_PATH']}
CLIENT_NAME={config['CLIENT_NAME']}
TIMEZONE={config['TIMEZONE']}
"""
    
    # 添加通用配置
    for key in ['DEFAULT_ADMIN_USER_IDS', 'DEFAULT_LANGUAGE', 'ADMIN_CHAT_ID', 'LOG_PATH']:
        if key in config and config[key]:
            env_content += f"{key}={config[key]}\n"
    
    env_file = Path(f".env.bot{bot_number}")
    env_file.write_text(env_content, encoding='utf-8')
    return env_file

def main():
    parser = argparse.ArgumentParser(description='启动指定编号的Bot')
    parser.add_argument('bot_number', type=int, help='Bot编号 (1, 2, 3, ...)')
    parser.add_argument('--config', type=str, default='.env.multi', help='配置文件路径')
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not Path(args.config).exists():
        print(f"❌ 配置文件不存在: {args.config}")
        print(f"请先创建配置文件，或使用 --config 指定配置文件")
        return 1
    
    # 加载配置
    config = load_bot_config(args.bot_number)
    if not config:
        return 1
    
    print(f"✅ 加载Bot {args.bot_number} 配置成功")
    print(f"   客户: {config['CLIENT_NAME']}")
    print(f"   数据库: {config['DB_PATH']}")
    print(f"   Token: {config['TOKEN'][:15]}...")
    
    # 创建临时.env文件
    env_file = create_env_file(config, args.bot_number)
    print(f"   配置文件: {env_file}")
    
    # 启动bot
    print(f"🚀 启动Bot {args.bot_number}...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['DB_PATH'] = config['DB_PATH']
        env['BOT_TOKEN'] = config['TOKEN']
        env['TZ'] = config['TIMEZONE']
        
        # 运行主程序
        cmd = [sys.executable, "src/app/main.py"]
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot {args.bot_number} 启动失败: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Bot {args.bot_number} 已停止")
    finally:
        # 清理临时文件
        if env_file.exists():
            env_file.unlink()
            print(f"🗑️  已清理临时配置文件")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())