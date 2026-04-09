#!/usr/bin/env python3
"""
M33 Lotto Bot Standard - 配置加载器
用于从指定目录加载配置
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化配置加载器
        
        参数:
            config_dir: 配置目录路径，如果为None则使用当前目录
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()
        self.config = {}
        
    def load(self) -> Dict[str, Any]:
        """加载所有配置"""
        self._load_env()
        self._load_settings()
        self._set_defaults()
        self._validate()
        return self.config
    
    def _load_env(self):
        """加载.env文件"""
        env_file = self.config_dir / ".env"
        
        if not env_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {env_file}")
        
        # 加载环境变量
        load_dotenv(env_file)
        
        # 读取关键配置
        self.config.update({
            'BOT_TOKEN': os.getenv('BOT_TOKEN'),
            'DB_PATH': os.getenv('DB_PATH', 'data/lotto.db'),
            'LOG_PATH': os.getenv('LOG_PATH', 'app.log'),
            'CLIENT_NAME': os.getenv('CLIENT_NAME', 'default_client'),
            'TIMEZONE': os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh'),
            'DEFAULT_LANGUAGE': os.getenv('DEFAULT_LANGUAGE', 'vi'),
            'BOT_DISPLAY_NAME': os.getenv('BOT_DISPLAY_NAME', 'M33 Lotto Bot'),
        })
        
        # 验证必要配置
        if not self.config['BOT_TOKEN'] or self.config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
            raise ValueError("BOT_TOKEN未配置或仍为模板值")
    
    def _load_settings(self):
        """加载settings.json文件"""
        settings_file = self.config_dir / "settings.json"
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.config['settings'] = settings
            except json.JSONDecodeError as e:
                print(f"警告: settings.json解析错误: {e}")
                self.config['settings'] = {}
        else:
            self.config['settings'] = {}
    
    def _set_defaults(self):
        """设置默认值"""
        defaults = {
            'features': {
                'enable_bet': True,
                'enable_report': True,
                'enable_settlement': True,
                'enable_admin': True,
            },
            'ui': {
                'currency_symbol': '₫',
                'date_format': 'YYYY-MM-DD',
            }
        }
        
        # 合并默认设置
        if 'settings' not in self.config:
            self.config['settings'] = {}
        
        for key, value in defaults.items():
            if key not in self.config['settings']:
                self.config['settings'][key] = value
            elif isinstance(value, dict):
                # 深度合并字典
                for sub_key, sub_value in value.items():
                    if sub_key not in self.config['settings'][key]:
                        self.config['settings'][key][sub_key] = sub_value
    
    def _validate(self):
        """验证配置"""
        required = ['BOT_TOKEN', 'DB_PATH']
        
        for key in required:
            if not self.config.get(key):
                raise ValueError(f"缺少必要配置: {key}")
        
        # 验证数据库路径
        db_path = Path(self.config['DB_PATH'])
        if not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def setup_environment(self):
        """设置环境变量"""
        # 设置数据库路径环境变量
        os.environ['DB_PATH'] = str(self.config['DB_PATH'])
        
        # 设置时区
        if 'TIMEZONE' in self.config:
            os.environ['TZ'] = self.config['TIMEZONE']
        
        # 设置日志路径
        if 'LOG_PATH' in self.config:
            log_path = Path(self.config['LOG_PATH'])
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def print_summary(self):
        """打印配置摘要"""
        print("=" * 50)
        print("M33 Lotto Bot Standard - 配置摘要")
        print("=" * 50)
        print(f"配置目录: {self.config_dir}")
        print(f"客户名称: {self.config.get('CLIENT_NAME', 'N/A')}")
        print(f"数据库路径: {self.config.get('DB_PATH', 'N/A')}")
        print(f"日志路径: {self.config.get('LOG_PATH', 'N/A')}")
        print(f"时区: {self.config.get('TIMEZONE', 'N/A')}")
        print(f"默认语言: {self.config.get('DEFAULT_LANGUAGE', 'N/A')}")
        print(f"Bot Token: {self.config.get('BOT_TOKEN', 'N/A')[:15]}...")
        print("=" * 50)

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='M33 Lotto Bot 配置加载器')
    parser.add_argument('--config-dir', type=str, help='配置目录路径')
    parser.add_argument('--check', action='store_true', help='仅检查配置，不启动')
    
    args = parser.parse_args()
    
    try:
        loader = ConfigLoader(args.config_dir)
        config = loader.load()
        
        if args.check:
            loader.print_summary()
            print("✅ 配置检查通过")
        else:
            loader.setup_environment()
            loader.print_summary()
            print("✅ 配置加载完成，可以启动Bot")
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())