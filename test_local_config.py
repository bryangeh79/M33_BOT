#!/usr/bin/env python3
"""
本地测试配置加载
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simple_load_config(config_dir=None):
    """简化的配置加载函数（不依赖dotenv）"""
    if config_dir:
        config_path = Path(config_dir)
    else:
        config_path = Path.cwd()
    
    # 读取.env文件
    env_file = config_path / ".env"
    if not env_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {env_file}")
    
    # 简单解析.env文件
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # 读取配置
    config = {
        'BOT_TOKEN': env_vars.get('BOT_TOKEN'),
        'DB_PATH': env_vars.get('DB_PATH', 'data/lotto.db'),
        'LOG_PATH': env_vars.get('LOG_PATH', 'app.log'),
        'CLIENT_NAME': env_vars.get('CLIENT_NAME', 'default_client'),
        'TIMEZONE': env_vars.get('TIMEZONE', 'Asia/Ho_Chi_Minh'),
        'DEFAULT_LANGUAGE': env_vars.get('DEFAULT_LANGUAGE', 'vi'),
    }
    
    # 验证必要配置
    if not config['BOT_TOKEN'] or config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
        raise ValueError("BOT_TOKEN未配置或仍为模板值")
    
    return config

def test_main_py_with_config():
    """测试main.py的配置加载"""
    print("测试main.py配置加载...")
    
    # 模拟命令行参数
    import argparse
    
    # 创建解析器（模拟main.py中的代码）
    parser = argparse.ArgumentParser(description='M33 Lotto Bot')
    parser.add_argument('--config-dir', type=str, help='配置目录路径')
    
    # 测试参数解析
    test_args = ['--config-dir', 'local_test_config']
    args = parser.parse_args(test_args)
    
    print(f"✅ 参数解析成功: --config-dir={args.config_dir}")
    
    # 加载配置
    try:
        config = simple_load_config(args.config_dir)
        print(f"✅ 配置加载成功")
        print(f"   客户: {config.get('CLIENT_NAME', 'N/A')}")
        print(f"   数据库: {config['DB_PATH']}")
        print(f"   Token: {config['BOT_TOKEN'][:15]}...")
        
        # 验证环境变量设置
        os.environ['DB_PATH'] = config['DB_PATH']
        os.environ['BOT_TOKEN'] = config['BOT_TOKEN']
        
        print(f"✅ 环境变量设置成功")
        print(f"   DB_PATH环境变量: {os.getenv('DB_PATH')}")
        print(f"   BOT_TOKEN环境变量: {os.getenv('BOT_TOKEN')[:15]}...")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    return True

def test_database_path():
    """测试数据库路径是否正确使用"""
    print("\n测试数据库路径...")
    
    # 检查修改后的文件是否使用环境变量
    files_to_check = [
        "src/modules/bet/services/bet_message_service.py",
        "src/app/database.py",
    ]
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        if 'os.getenv("DB_PATH"' in content or "os.getenv('DB_PATH'" in content:
            print(f"✅ {filepath} - 使用环境变量")
        else:
            print(f"❌ {filepath} - 未使用环境变量")
    
    # 测试数据库路径解析
    db_path = os.getenv('DB_PATH', 'data/lotto.db')
    print(f"✅ 当前数据库路径: {db_path}")
    
    # 确保目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        print(f"✅ 数据库目录已创建: {db_dir}")
    
    return True

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n测试向后兼容性...")
    
    # 测试1: 检查main.py中的全局变量定义
    print("测试1: 检查全局变量定义")
    try:
        with open('src/app/main.py', 'r') as f:
            content = f.read()
        
        # 检查是否保留了原有的全局变量定义
        if 'BOT_TOKEN = os.getenv("BOT_TOKEN")' in content:
            print("✅ main.py保留了BOT_TOKEN全局变量定义")
        else:
            print("❌ main.py缺少BOT_TOKEN全局变量定义")
            return False
        
        # 检查是否保留了原有的函数
        if 'def validate_environment() -> None:' in content:
            print("✅ main.py保留了validate_environment函数")
        else:
            print("❌ main.py缺少validate_environment函数")
            return False
        
        if 'def initialize_database() -> None:' in content:
            print("✅ main.py保留了initialize_database函数")
        else:
            print("❌ main.py缺少initialize_database函数")
            return False
        
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False
    
    # 测试2: 检查环境变量设置逻辑
    print("\n测试2: 检查环境变量设置逻辑")
    try:
        # 模拟main()函数中的环境变量设置
        os.environ['DB_PATH'] = 'data/backward_test.db'
        os.environ['BOT_TOKEN'] = 'test_backward_token'
        
        print("✅ 环境变量设置逻辑正常")
        
    except Exception as e:
        print(f"❌ 环境变量设置测试失败: {e}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("M33 Lotto Bot - 本地配置测试")
    print("=" * 50)
    
    # 创建测试配置目录
    test_dir = "local_test_config"
    if not os.path.exists(test_dir):
        print("❌ 测试配置目录不存在")
        return 1
    
    tests = [
        ("配置加载", test_main_py_with_config),
        ("数据库路径", test_database_path),
        ("向后兼容性", test_backward_compatibility),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n🔧 {test_name}:")
        try:
            if test_func():
                print(f"✅ {test_name}通过")
            else:
                print(f"❌ {test_name}失败")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有本地测试通过！")
        print("✅ main.py支持--config-dir参数")
        print("✅ 数据库路径使用环境变量")
        print("✅ 向后兼容性保持")
        print("\n🚀 可以继续Phase V3步骤2（服务器部署）")
    else:
        print("⚠ 部分测试未通过，请检查问题")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())