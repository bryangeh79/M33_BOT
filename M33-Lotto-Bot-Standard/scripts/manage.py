#!/usr/bin/env python3
"""
M33 Lotto Bot Standard - 智能管理脚本
版本: 1.0.0

功能：批量/个别管理所有客户
用法：python manage.py <命令> [客户编号...]
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_color(color, icon, msg):
    print(f"{color}{icon} {msg}{Colors.END}")

def print_success(msg):
    print_color(Colors.GREEN, "✅", msg)

def print_error(msg):
    print_color(Colors.RED, "❌", msg)

def print_info(msg):
    print_color(Colors.BLUE, "ℹ️", msg)

def print_warning(msg):
    print_color(Colors.YELLOW, "⚠️", msg)

def print_status(msg):
    print_color(Colors.CYAN, "📊", msg)

def print_action(msg):
    print_color(Colors.MAGENTA, "🚀", msg)

def run_command(cmd, capture_output=True):
    """执行Shell命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def get_active_clients():
    """获取所有已激活的客户"""
    active = []
    base_dir = Path("/opt/M33-Lotto-Bot-Standard")
    
    for i in range(1, 11):
        client_id = f"{i:02d}"
        env_file = base_dir / "configs" / f"client_{client_id}" / ".env"
        
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    # 检查是否有真实Token（不是模板）
                    if "BOT_TOKEN=" in content and "YOUR_BOT_TOKEN_HERE" not in content:
                        active.append(client_id)
            except:
                continue
    
    return active

def get_client_info(client_id):
    """获取客户信息"""
    base_dir = Path("/opt/M33-Lotto-Bot-Standard")
    env_file = base_dir / "configs" / f"client_{client_id}" / ".env"
    
    if not env_file.exists():
        return None
    
    info = {"id": client_id, "activated": False}
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("BOT_TOKEN="):
                    token = line.strip().split('=', 1)[1]
                    info["activated"] = token != "YOUR_BOT_TOKEN_HERE" and token != ""
                    info["token_preview"] = token[:10] + "..." if len(token) > 10 else token
                elif line.startswith("CLIENT_NAME="):
                    info["name"] = line.strip().split('=', 1)[1]
                elif line.startswith("# 激活时间:"):
                    info["activated_at"] = line.strip().replace("# 激活时间: ", "")
    except:
        pass
    
    return info

def start_client(client_id):
    """启动单个客户"""
    cmd = f"sudo supervisorctl start m33-standard-client-{client_id}"
    success, out, err = run_command(cmd)
    
    if success:
        print_success(f"客户 {client_id} 已启动")
        return True
    else:
        if "already started" in err.lower():
            print_warning(f"客户 {client_id} 已在运行中")
            return True
        else:
            print_error(f"客户 {client_id} 启动失败: {err.strip()}")
            return False

def stop_client(client_id):
    """停止单个客户"""
    cmd = f"sudo supervisorctl stop m33-standard-client-{client_id}"
    success, out, err = run_command(cmd)
    
    if success:
        print_success(f"客户 {client_id} 已停止")
        return True
    else:
        if "not running" in err.lower():
            print_warning(f"客户 {client_id} 未在运行")
            return True
        else:
            print_error(f"客户 {client_id} 停止失败: {err.strip()}")
            return False

def restart_client(client_id):
    """重启单个客户"""
    cmd = f"sudo supervisorctl restart m33-standard-client-{client_id}"
    success, out, err = run_command(cmd)
    
    if success:
        print_success(f"客户 {client_id} 已重启")
        return True
    else:
        print_error(f"客户 {client_id} 重启失败: {err.strip()}")
        return False

def status_client(client_id):
    """查看单个客户状态"""
    cmd = f"sudo supervisorctl status m33-standard-client-{client_id}"
    success, out, err = run_command(cmd)
    
    info = get_client_info(client_id)
    
    if info and info["activated"]:
        status_color = Colors.GREEN
        status_text = "已激活"
    elif info:
        status_color = Colors.YELLOW
        status_text = "未激活"
    else:
        status_color = Colors.RED
        status_text = "配置缺失"
    
    print(f"{Colors.BOLD}客户 {client_id}:{Colors.END} [{status_color}{status_text}{Colors.END}]")
    
    if info and info.get("activated_at"):
        print(f"  激活时间: {info['activated_at']}")
    
    if success:
        status_line = out.strip()
        if "RUNNING" in status_line:
            print(f"  进程状态: {Colors.GREEN}{status_line}{Colors.END}")
        elif "STOPPED" in status_line or "FATAL" in status_line:
            print(f"  进程状态: {Colors.RED}{status_line}{Colors.END}")
        else:
            print(f"  进程状态: {status_line}")
    else:
        print(f"  进程状态: {Colors.RED}未运行或未配置{Colors.END}")
    
    print()

def start_all_clients():
    """启动所有已激活客户"""
    active_clients = get_active_clients()
    
    if not active_clients:
        print_warning("没有已激活的客户")
        return
    
    print_action(f"启动所有已激活客户 ({len(active_clients)}个)...")
    print()
    
    success_count = 0
    for client_id in active_clients:
        if start_client(client_id):
            success_count += 1
    
    print()
    print_success(f"启动完成：{success_count}/{len(active_clients)} 个客户启动成功")

def stop_all_clients():
    """停止所有客户"""
    # 获取所有配置了的客户（包括未激活但已配置的）
    all_clients = []
    for i in range(1, 11):
        client_id = f"{i:02d}"
        env_file = Path(f"/opt/M33-Lotto-Bot-Standard/configs/client_{client_id}/.env")
        if env_file.exists():
            all_clients.append(client_id)
    
    if not all_clients:
        print_warning("没有配置的客户")
        return
    
    print_action(f"停止所有客户 ({len(all_clients)}个)...")
    print()
    
    success_count = 0
    for client_id in all_clients:
        if stop_client(client_id):
            success_count += 1
    
    print()
    print_success(f"停止完成：{success_count}/{len(all_clients)} 个客户停止成功")

def restart_all_clients():
    """重启所有客户"""
    active_clients = get_active_clients()
    
    if not active_clients:
        print_warning("没有已激活的客户")
        return
    
    print_action(f"重启所有已激活客户 ({len(active_clients)}个)...")
    print()
    
    success_count = 0
    for client_id in active_clients:
        if restart_client(client_id):
            success_count += 1
    
    print()
    print_success(f"重启完成：{success_count}/{len(active_clients)} 个客户重启成功")

def status_all_clients():
    """查看所有客户状态"""
    print_status("所有客户状态")
    print("=" * 50)
    print()
    
    total = 0
    active = 0
    running = 0
    
    for i in range(1, 11):
        client_id = f"{i:02d}"
        info = get_client_info(client_id)
        
        if info:
            total += 1
            if info["activated"]:
                active += 1
            
            # 检查进程状态
            cmd = f"sudo supervisorctl status m33-standard-client-{client_id}"
            success, out, err = run_command(cmd)
            if success and "RUNNING" in out:
                running += 1
        
        status_client(client_id)
    
    print("=" * 50)
    print(f"{Colors.BOLD}统计信息：{Colors.END}")
    print(f"  总配置席位: {total}/10")
    print(f"  已激活客户: {active}")
    print(f"  运行中客户: {running}")
    print()

def show_system_info():
    """显示系统信息"""
    print_status("M33 Lotto Bot Standard 系统信息")
    print("=" * 50)
    
    # 安装目录
    base_dir = Path("/opt/M33-Lotto-Bot-Standard")
    if base_dir.exists():
        print(f"{Colors.BOLD}安装目录:{Colors.END} {base_dir}")
    else:
        print_error("系统未安装或安装目录不存在")
        return
    
    # 数据库目录
    data_dir = base_dir / "data"
    if data_dir.exists():
        db_files = list(data_dir.glob("*.db"))
        print(f"{Colors.BOLD}数据库文件:{Colors.END} {len(db_files)} 个")
    
    # 日志目录
    log_dir = Path("/var/log/m33-standard")
    if log_dir.exists():
        print(f"{Colors.BOLD}日志目录:{Colors.END} {log_dir}")
    
    # Supervisor状态
    success, out, err = run_command("sudo supervisorctl status m33-standard-client-*")
    if success:
        lines = [line for line in out.strip().split('\n') if line]
        print(f"{Colors.BOLD}Supervisor进程:{Colors.END} {len(lines)} 个")
    
    print()

def show_help():
    """显示帮助信息"""
    print(f"{Colors.BOLD}M33 Lotto Bot Standard - 智能管理脚本{Colors.END}")
    print("版本: 1.0.0")
    print()
    print(f"{Colors.BOLD}用法：{Colors.END}")
    print("  python manage.py <命令> [客户编号...]")
    print()
    print(f"{Colors.BOLD}命令列表：{Colors.END}")
    print(f"  {Colors.GREEN}start{Colors.END}     启动客户")
    print(f"  {Colors.RED}stop{Colors.END}      停止客户")
    print(f"  {Colors.YELLOW}restart{Colors.END}   重启客户")
    print(f"  {Colors.CYAN}status{Colors.END}    查看客户状态")
    print(f"  {Colors.MAGENTA}start-all{Colors.END}  启动所有已激活客户")
    print(f"  {Colors.MAGENTA}stop-all{Colors.END}   停止所有客户")
    print(f"  {Colors.MAGENTA}restart-all{Colors.END} 重启所有已激活客户")
    print(f"  {Colors.MAGENTA}status-all{Colors.END}  查看所有客户状态")
    print(f"  {Colors.BLUE}info{Colors.END}      显示系统信息")
    print(f"  {Colors.BLUE}help{Colors.END}      显示此帮助信息")
    print()
    print(f"{Colors.BOLD}示例：{Colors.END}")
    print("  python manage.py start 01           # 启动客户01")
    print("  python manage.py start 01 02 03     # 启动客户01,02,03")
    print("  python manage.py stop-all           # 停止所有客户")
    print("  python manage.py status-all         # 查看所有状态")
    print("  python manage.py restart 02         # 重启客户02")
    print()
    print(f"{Colors.BOLD}客户编号：{Colors.END}")
    print("  01-10: 预配置的10个客户席位")
    print()
    print(f"{Colors.BOLD}注意事项：{Colors.END}")
    print("  - 需要sudo权限执行Supervisor命令")
    print("  - start-all 只启动已激活的客户")
    print("  - 客户激活使用 activate.py 脚本")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    # 处理帮助命令
    if command in ['-h', '--help', 'help']:
        show_help()
        return
    
    # 处理系统信息命令
    if command == 'info':
        show_system_info()
        return
    
    # 处理批量命令
    if command == 'start-all':
        start_all_clients()
        return
    
    if command == 'stop-all':
        stop_all_clients()
        return
    
    if command == 'restart-all':
        restart_all_clients()
        return
    
    if command == 'status-all':
        status_all_clients()
        return
    
    # 处理需要客户编号的命令
    if command not in ['start', 'stop', 'restart', 'status']:
        print_error(f"未知命令：{command}")
        print()
        show_help()
        return
    
    if len(sys.argv) < 3:
        print_error(f"命令 '{command}' 需要指定客户编号")
        print()
        print(f"示例：python manage.py {command} 01")
        print(f"       python manage.py {command} 01 02 03")
        return
    
    client_ids = sys.argv[2:]
    
    # 验证客户编号
    valid_ids = []
    for client_id in client_ids:
        if client_id.isdigit() and 1 <= int(client_id) <= 10:
            valid_ids.append(client_id.zfill(2))
        else:
            print_warning(f"忽略无效客户编号：{client_id}（必须是01-10）")
    
    if not valid_ids:
        print_error("没有有效的客户编号")
        return
    
    # 执行命令
    print_action(f"执行命令：{command} {' '.join(valid_ids)}")
    print()
    
    success_count = 0
    for client_id in valid_ids:
        if command == 'start':
            if start_client(client_id):
                success_count += 1
        elif command == 'stop':
            if stop_client(client_id):
                success_count += 1
        elif command == 'restart':
            if restart_client(client_id):
                success_count += 1
        elif command == 'status':
            status_client(client_id)
            success_count += 1
    
    if command != 'status':
        print()
        print_success(f"命令执行完成：{success_count}/{len(valid_ids)} 个客户成功")

if __name__ == "__main__":
    main()