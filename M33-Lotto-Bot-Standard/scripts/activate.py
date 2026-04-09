#!/usr/bin/env python3
"""
M33 Lotto Bot Standard - 客户激活脚本
版本: 1.0.0

功能：一键激活客户，只需提供Bot Token
用法：python activate.py <客户编号> <Bot_Token>
示例：python activate.py 01 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def validate_token(token):
    """验证Bot Token格式"""
    # Telegram Bot Token格式: 数字:字母数字组合
    pattern = r'^\d{9,10}:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))

def validate_client_id(client_id):
    """验证客户编号"""
    return client_id.isdigit() and 1 <= int(client_id) <= 10

def activate_client(client_id, bot_token):
    """
    激活指定客户
    参数：
        client_id: 客户编号 (01-10)
        bot_token: Telegram Bot Token
    """
    # 标准化客户编号（确保两位数字）
    client_id = client_id.zfill(2)
    
    print(f"{Colors.BOLD}🔧 激活客户 {client_id}...{Colors.END}")
    print(f"    Token: {bot_token[:15]}...")
    
    # 检查客户编号有效性
    if not validate_client_id(client_id):
        print_error(f"客户编号无效：{client_id}，必须是01-10")
        return False
    
    # 检查Token格式
    if not validate_token(bot_token):
        print_warning("Token格式可能不正确，但仍继续激活...")
        print_info("正确格式：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    # 定义路径
    base_dir = Path("/opt/M33-Lotto-Bot-Standard")
    config_dir = base_dir / "configs" / f"client_{client_id}"
    template_file = config_dir / ".env.template"
    env_file = config_dir / ".env"
    db_file = base_dir / "data" / f"client_{client_id}.db"
    
    # 检查配置文件是否存在
    if not template_file.exists():
        print_error(f"配置文件不存在：{template_file}")
        print_info("请先运行 setup.sh 安装系统")
        return False
    
    # 读取模板
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_error(f"读取模板文件失败：{e}")
        return False
    
    # 替换Token
    if "YOUR_BOT_TOKEN_HERE" in content:
        content = content.replace("YOUR_BOT_TOKEN_HERE", bot_token)
    else:
        # 如果模板中没有占位符，直接替换BOT_TOKEN行
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith("BOT_TOKEN="):
                new_lines.append(f"BOT_TOKEN={bot_token}")
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    
    # 添加激活时间戳
    activated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content += f"\n# 激活时间: {activated_at}\n"
    
    # 写入正式配置文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f"配置文件已生成：{env_file}")
    except Exception as e:
        print_error(f"写入配置文件失败：{e}")
        return False
    
    # 检查数据库文件
    if not db_file.exists():
        print_warning(f"数据库文件不存在，将创建：{db_file}")
        try:
            db_file.touch()
            print_success("数据库文件已创建")
        except Exception as e:
            print_error(f"创建数据库文件失败：{e}")
            return False
    
    # 设置文件权限
    try:
        os.chmod(env_file, 0o600)  # 只允许所有者读写
        print_success("文件权限已设置")
    except Exception as e:
        print_warning(f"设置文件权限失败：{e}")
    
    # 生成激活报告
    print(f"\n{Colors.BOLD}📋 激活完成报告{Colors.END}")
    print("=" * 40)
    print(f"客户编号: {client_id}")
    print(f"配置文件: {env_file}")
    print(f"数据库文件: {db_file}")
    print(f"日志目录: /var/log/m33-standard/client_{client_id}/")
    print(f"激活时间: {activated_at}")
    print("=" * 40)
    
    return True

def show_help():
    """显示帮助信息"""
    print(f"{Colors.BOLD}M33 Lotto Bot Standard - 客户激活脚本{Colors.END}")
    print("版本: 1.0.0")
    print()
    print(f"{Colors.BOLD}用法：{Colors.END}")
    print("  python activate.py <客户编号> <Bot_Token>")
    print()
    print(f"{Colors.BOLD}参数：{Colors.END}")
    print("  客户编号: 01-10（对应10个预配置席位）")
    print("  Bot_Token: Telegram Bot Token，格式为 数字:字母数字组合")
    print()
    print(f"{Colors.BOLD}示例：{Colors.END}")
    print("  python activate.py 01 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("  python activate.py 02 9876543210:ZYXwvutsRQponmlkjiHGFEdcba")
    print()
    print(f"{Colors.BOLD}获取Token：{Colors.END}")
    print("  1. 在Telegram中联系 @BotFather")
    print("  2. 发送 /newbot 创建新机器人")
    print("  3. 设置机器人名称和用户名")
    print("  4. 复制生成的Token")
    print()
    print(f"{Colors.BOLD}注意事项：{Colors.END}")
    print("  - 每个客户需要独立的Bot Token")
    print("  - 激活后使用 manage.py 启动服务")
    print("  - 客户编号01-10对应预配置席位")

def main():
    """主函数"""
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    if len(sys.argv) != 3:
        print_error("参数错误！")
        print()
        show_help()
        sys.exit(1)
    
    client_id = sys.argv[1]
    bot_token = sys.argv[2]
    
    print(f"{Colors.BOLD}=========================================={Colors.END}")
    print(f"{Colors.BOLD}🚀 M33 Lotto Bot Standard 客户激活{Colors.END}")
    print(f"{Colors.BOLD}=========================================={Colors.END}")
    print()
    
    if activate_client(client_id, bot_token):
        print()
        print_success(f"客户 {client_id} 激活成功！")
        print()
        print(f"{Colors.BOLD}📋 下一步操作：{Colors.END}")
        print("1. 启动客户服务：")
        print(f"   python manage.py start {client_id}")
        print()
        print("2. 验证运行状态：")
        print(f"   python manage.py status {client_id}")
        print()
        print("3. 查看实时日志：")
        print(f"   tail -f /var/log/m33-standard/client_{client_id}/stdout.log")
        print()
        print("4. 创建Telegram群聊并添加Bot：")
        print(f"   - 创建新群聊")
        print(f"   - 添加 @你的机器人用户名")
        print(f"   - 邀请客户加入")
        print()
        print(f"{Colors.GREEN}💡 提示：使用 manage.py 脚本管理所有客户{Colors.END}")
    else:
        print_error("激活失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()