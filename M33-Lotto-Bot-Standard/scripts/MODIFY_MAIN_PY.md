# 修改 main.py 支持多租户配置

## 目标
修改现有的 `src/app/main.py` 文件，使其支持从指定配置目录加载设置。

## 修改步骤

### 1. 在文件顶部添加导入和参数解析

在 `main.py` 的开头（在所有导入之后），添加以下代码：

```python
# ===========================================
# 多租户配置支持
# ===========================================
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
import json

def load_config(config_dir=None):
    """
    从指定目录加载配置
    
    参数:
        config_dir: 配置目录路径，如果为None则使用当前目录
    
    返回:
        dict: 配置字典
    """
    if config_dir:
        config_path = Path(config_dir)
    else:
        config_path = Path.cwd()
    
    # 加载.env文件
    env_file = config_path / ".env"
    if not env_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {env_file}")
    
    load_dotenv(env_file)
    
    # 读取配置
    config = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'DB_PATH': os.getenv('DB_PATH', 'data/lotto.db'),
        'LOG_PATH': os.getenv('LOG_PATH', 'app.log'),
        'CLIENT_NAME': os.getenv('CLIENT_NAME', 'default_client'),
        'TIMEZONE': os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh'),
        'DEFAULT_LANGUAGE': os.getenv('DEFAULT_LANGUAGE', 'vi'),
    }
    
    # 验证必要配置
    if not config['BOT_TOKEN'] or config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
        raise ValueError("BOT_TOKEN未配置或仍为模板值")
    
    # 加载settings.json（可选）
    settings_file = config_path / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                config['settings'] = json.load(f)
        except json.JSONDecodeError:
            config['settings'] = {}
    else:
        config['settings'] = {}
    
    return config
```

### 2. 修改主函数入口

找到 `main.py` 中的主函数（通常是 `def main():` 或文件末尾的代码块），修改为：

```python
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='M33 Lotto Bot')
    parser.add_argument('--config-dir', type=str, help='配置目录路径')
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config_dir)
        
        # 设置环境变量
        os.environ['DB_PATH'] = config['DB_PATH']
        
        # 设置时区
        if 'TIMEZONE' in config:
            os.environ['TZ'] = config['TIMEZONE']
        
        # 验证Bot Token
        bot_token = config['BOT_TOKEN']
        if not bot_token:
            print("错误: BOT_TOKEN未配置")
            return
        
        print(f"✅ 配置加载完成")
        print(f"   客户: {config.get('CLIENT_NAME', 'N/A')}")
        print(f"   数据库: {config['DB_PATH']}")
        print(f"   Token: {bot_token[:15]}...")
        
        # 设置日志（如果需要）
        if 'LOG_PATH' in config:
            import logging
            logging.basicConfig(
                filename=config['LOG_PATH'],
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # 这里继续原有的启动代码...
        # 确保使用 config['BOT_TOKEN'] 而不是硬编码的TOKEN
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    # 原有的Application创建和启动代码
    # 修改 Application.builder().token(...) 使用 config['BOT_TOKEN']
```

### 3. 修改Bot Token引用

在代码中找到所有使用硬编码Bot Token的地方，改为使用配置：

```python
# 原来的代码：
# application = Application.builder().token("YOUR_BOT_TOKEN").build()

# 修改为：
application = Application.builder().token(config['BOT_TOKEN']).build()
```

### 4. 修改数据库连接

找到数据库连接代码，确保使用配置的DB_PATH：

```python
# 原来的代码可能使用固定路径
# 修改为使用环境变量或配置

# 方法A：通过环境变量（推荐）
# 在 load_config 函数中已经设置了 os.environ['DB_PATH']
# 然后在数据库连接代码中使用 os.getenv('DB_PATH')

# 方法B：直接传递配置
# 修改数据库连接函数，接受db_path参数
```

### 5. 完整的修改示例

以下是 `main.py` 修改后的完整结构示例：

```python
#!/usr/bin/env python3
"""
M33 Lotto Bot - 主程序
支持多租户配置
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# 原有的导入...
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
# ... 其他导入

def load_config(config_dir=None):
    """加载配置（同上）"""
    # ... 实现同上

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='M33 Lotto Bot')
    parser.add_argument('--config-dir', type=str, help='配置目录路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config_dir)
    bot_token = config['BOT_TOKEN']
    
    # 设置环境变量
    os.environ['DB_PATH'] = config['DB_PATH']
    
    # 创建Application
    application = Application.builder().token(bot_token).build()
    
    # 注册处理器（原有代码）
    # ...
    
    # 启动Bot
    print(f"🚀 启动M33 Lotto Bot (客户: {config.get('CLIENT_NAME', 'N/A')})")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

## 验证修改

### 1. 测试配置加载
```bash
cd /opt/M33-Lotto-Bot-Standard
python scripts/config_loader.py --config-dir configs/client_01 --check
```

### 2. 测试启动
```bash
# 使用配置启动
python src/app/main.py --config-dir configs/client_01
```

### 3. 验证数据库连接
确保数据库文件正确创建在指定路径。

## 注意事项

1. **向后兼容**：保持原有单实例运行方式
   - 不提供 `--config-dir` 参数时，使用当前目录的 `.env` 文件
   - 或者使用默认配置

2. **错误处理**：配置加载失败时提供清晰错误信息

3. **日志分离**：每个客户应有独立的日志文件

4. **环境隔离**：确保不同客户的进程环境完全独立

## 快速修改脚本

如果你需要快速修改现有 `main.py`，可以使用以下脚本：

```bash
# 备份原文件
cp src/app/main.py src/app/main.py.backup

# 使用sed进行快速修改（示例）
sed -i "s/Application\.builder()\.token(\".*\")/Application.builder().token(config['BOT_TOKEN'])/g" src/app/main.py
```

## 支持

如果修改遇到问题，可以：
1. 查看错误日志
2. 检查配置文件格式
3. 验证文件权限
4. 确保所有依赖已安装

完成修改后，M33 Lotto Bot Standard 系统就可以正常工作了！