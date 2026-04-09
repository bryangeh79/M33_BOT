#!/usr/bin/env python3
"""
Bot配置设置脚本
根据 .env.multi 文件创建各个bot的配置目录
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

def load_bot_configs():
    """从 .env.multi 加载所有bot配置"""
    env_file = Path(".env.multi")
    if not env_file.exists():
        print(f"❌ 配置文件不存在: {env_file}")
        return {}
    
    bots = {}
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析配置行
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 检查是否是bot特定配置
                if key.startswith('BOT_'):
                    # 解析格式: BOT_<编号>_<配置项>
                    parts = key.split('_')
                    if len(parts) >= 3 and parts[1].isdigit():
                        bot_num = int(parts[1])
                        config_key = '_'.join(parts[2:])  # 获取配置项名称
                        
                        if bot_num not in bots:
                            bots[bot_num] = {}
                        
                        bots[bot_num][config_key] = value
                # 通用配置 - 添加到所有bot
                else:
                    for bot_num in bots:
                        bots[bot_num][key] = value
    
    return bots

def create_bot_config(bot_number, config):
    """为单个bot创建配置目录"""
    bot_dir = Path(f"configs/bot_{bot_number}")
    bot_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建.env文件
    env_content = f"""# Bot {bot_number} 配置
BOT_TOKEN={config.get('TOKEN', '')}
DB_PATH={config.get('DB_PATH', f'data/bot{bot_number}.db')}
CLIENT_NAME={config.get('CLIENT_NAME', f'bot{bot_number}')}
TIMEZONE={config.get('TIMEZONE', 'Asia/Ho_Chi_Minh')}
"""
    
    # 添加通用配置
    for key in ['DEFAULT_ADMIN_USER_IDS', 'DEFAULT_LANGUAGE', 'ADMIN_CHAT_ID', 'LOG_PATH']:
        if key in config and config[key]:
            env_content += f"{key}={config[key]}\n"
    
    env_file = bot_dir / ".env"
    env_file.write_text(env_content, encoding='utf-8')
    
    # 复制settings.json模板（如果存在）
    settings_template = Path("M33-Lotto-Bot-Standard/configs/client_01/settings.json")
    if settings_template.exists():
        shutil.copy(settings_template, bot_dir / "settings.json")
    
    return bot_dir

def main():
    parser = argparse.ArgumentParser(description='设置Bot配置目录')
    parser.add_argument('--list', action='store_true', help='列出所有已配置的bot')
    parser.add_argument('--setup', type=int, nargs='*', help='设置指定编号的bot（不指定则设置所有）')
    parser.add_argument('--clean', action='store_true', help='清理所有配置目录')
    args = parser.parse_args()
    
    # 清理模式
    if args.clean:
        configs_dir = Path("configs")
        if configs_dir.exists():
            shutil.rmtree(configs_dir)
            print("✅ 已清理所有配置目录")
        return 0
    
    # 加载配置
    bots = load_bot_configs()
    
    if not bots:
        print("❌ 没有找到任何bot配置")
        print("请检查 .env.multi 文件格式是否正确")
        return 1
    
    # 列出模式
    if args.list:
        print(f"📋 找到 {len(bots)} 个bot配置:")
        for bot_num in sorted(bots.keys()):
            config = bots[bot_num]
            token = config.get('TOKEN', '未配置')
            if token:
                token_display = f"{token[:15]}..." if len(token) > 15 else token
            else:
                token_display = "未配置"
            
            print(f"  Bot {bot_num}:")
            print(f"    名称: {config.get('CLIENT_NAME', 'N/A')}")
            print(f"    Token: {token_display}")
            print(f"    数据库: {config.get('DB_PATH', 'N/A')}")
            print(f"    时区: {config.get('TIMEZONE', 'N/A')}")
            print()
        return 0
    
    # 设置模式
    bots_to_setup = args.setup if args.setup else sorted(bots.keys())
    
    print(f"🔧 开始设置 {len(bots_to_setup)} 个bot...")
    
    for bot_num in bots_to_setup:
        if bot_num not in bots:
            print(f"❌ Bot {bot_num} 在配置文件中未找到")
            continue
        
        config = bots[bot_num]
        
        # 检查token是否配置
        if not config.get('TOKEN'):
            print(f"⚠️  Bot {bot_num} 的TOKEN未配置，跳过")
            continue
        
        bot_dir = create_bot_config(bot_num, config)
        print(f"✅ Bot {bot_num} 配置已创建: {bot_dir}")
    
    print("\n🎉 配置完成!")
    print("\n启动命令:")
    for bot_num in bots_to_setup:
        if bot_num in bots and bots[bot_num].get('TOKEN'):
            print(f"  Bot {bot_num}: python src/app/main.py --config-dir configs/bot_{bot_num}")
    
    print("\n批量启动所有bot:")
    print("  python start_all_bots_simple.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())