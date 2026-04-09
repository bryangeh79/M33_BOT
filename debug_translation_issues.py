#!/usr/bin/env python3
"""
检查翻译问题
"""

import os
import re

def find_hardcoded_english():
    """查找硬编码的英文文本"""
    print("=== 查找硬编码英文文本 ===")
    
    # 搜索src目录下的.py文件
    src_dir = "src"
    
    # 常见的英文关键词（在中文/越南语系统中不应该出现）
    english_keywords = [
        "Settlement Report",
        "Transaction Report", 
        "Number Detail Report",
        "Over Limit Report",
        "Date:",
        "Total:",
        "Amount:",
        "Region:",
        "Ticket No:",
        "Bet Type:",
        "Numbers:",
        "Unit:",
        "Total Settlement",
        "Winning Details",
        "Generated at:",
        "Select region:",
        "Select date:",
        "Please enter",
        "Invalid",
        "Error:",
        "Success:",
        "Back",
        "Close",
        "Refresh",
        "Export",
        "Report",
        "Result",
        "Admin",
        "Info"
    ]
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 跳过翻译文件
                    if 'i18n' in filepath or 'translator' in filepath:
                        continue
                    
                    found = []
                    for keyword in english_keywords:
                        if keyword in content:
                            # 检查是否在t()函数调用中
                            if f't("{keyword}' not in content and f"t('{keyword}" not in content:
                                found.append(keyword)
                    
                    if found:
                        print(f"\n📄 {filepath}")
                        print(f"   硬编码英文: {', '.join(found[:5])}")
                        
                        # 显示示例行
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if any(keyword in line for keyword in found[:3]):
                                if len(line) > 100:
                                    line = line[:100] + "..."
                                print(f"   第{i+1}行: {line.strip()}")
                                break
                            
                except Exception as e:
                    print(f"❌ 读取文件错误 {filepath}: {e}")

def check_html_templates():
    """检查HTML模板"""
    print("\n=== 检查HTML模板 ===")
    
    html_files = [
        "src/modules/report/formatters/report_html_formatter.py",
        "src/modules/report/formatters/settlement_report_html_exporter.py",
        "src/modules/report/formatters/over_limit_report_html_exporter.py",
        "src/modules/report/formatters/transaction_report_formatter_html.py"
    ]
    
    for filepath in html_files:
        if os.path.exists(filepath):
            print(f"\n📄 {filepath}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查<html lang="en">
                if '<html lang="en">' in content:
                    print("   ❌ 硬编码: <html lang=\"en\">")
                
                # 检查硬编码英文标题
                title_patterns = [
                    r'<h1[^>]*>([^<]+)</h1>',
                    r'<title[^>]*>([^<]+)</title>',
                    r'class="title"[^>]*>([^<]+)<',
                    r'class="meta"[^>]*>([^<]+)<'
                ]
                
                for pattern in title_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        match = match.strip()
                        # 跳过空的和可能是变量的内容
                        if match and not match.startswith('{') and len(match) < 100:
                            print(f"   可能硬编码: {match}")
                
            except Exception as e:
                print(f"   ❌ 读取错误: {e}")
        else:
            print(f"⚠️ 文件不存在: {filepath}")

def check_translation_coverage():
    """检查翻译覆盖"""
    print("\n=== 检查翻译覆盖 ===")
    
    # 检查en.py中的键是否在其他语言文件中都有
    en_file = "src/i18n/en.py"
    vi_file = "src/i18n/vi.py"
    zh_file = "src/i18n/zh.py"
    
    try:
        # 读取en.py中的键
        with open(en_file, 'r', encoding='utf-8') as f:
            en_content = f.read()
        
        # 提取STRINGS字典中的键
        import ast
        tree = ast.parse(en_content)
        
        en_keys = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for key_node, value_node in zip(node.keys, node.values):
                    if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                        en_keys.add(key_node.value)
        
        print(f"英文翻译键数量: {len(en_keys)}")
        
        # 检查vi.py
        if os.path.exists(vi_file):
            with open(vi_file, 'r', encoding='utf-8') as f:
                vi_content = f.read()
            
            vi_tree = ast.parse(vi_content)
            vi_keys = set()
            for node in ast.walk(vi_tree):
                if isinstance(node, ast.Dict):
                    for key_node, value_node in zip(node.keys, node.values):
                        if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                            vi_keys.add(key_node.value)
            
            missing_in_vi = en_keys - vi_keys
            print(f"越南语翻译键数量: {len(vi_keys)}")
            print(f"越南语缺失键: {len(missing_in_vi)}")
            if missing_in_vi:
                print(f"   示例缺失键: {list(missing_in_vi)[:5]}")
        
    except Exception as e:
        print(f"❌ 分析错误: {e}")

def check_t_function_usage():
    """检查t()函数使用情况"""
    print("\n=== 检查t()函数使用 ===")
    
    src_dir = "src"
    t_function_pattern = r't\([^)]+\)'
    
    total_files = 0
    files_without_t = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py') and 'i18n' not in root and 'test' not in root:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 跳过翻译相关文件
                    if 'translator' in filepath or file in ['en.py', 'vi.py', 'zh.py']:
                        continue
                    
                    total_files += 1
                    
                    # 检查是否包含用户可见文本但没有使用t()
                    if '"' in content or "'" in content:
                        # 查找可能的用户可见文本
                        string_pattern = r'["\']([^"\']{5,50})["\']'
                        strings = re.findall(string_pattern, content)
                        
                        user_visible_strings = []
                        for s in strings:
                            # 过滤掉可能是代码标识符的字符串
                            if (any(c.isalpha() for c in s) and 
                                not s.startswith('http') and
                                not s.startswith('data/') and
                                not s.endswith('.db') and
                                not s.endswith('.py') and
                                'import' not in content.split(s)[0][-100:]):
                                user_visible_strings.append(s)
                        
                        if user_visible_strings and not re.search(t_function_pattern, content):
                            files_without_t.append((filepath, user_visible_strings[:3]))
                            
                except Exception as e:
                    pass
    
    print(f"检查文件数: {total_files}")
    print(f"可能未使用t()的文件: {len(files_without_t)}")
    
    if files_without_t:
        print("\n可能有问题文件:")
        for filepath, strings in files_without_t[:5]:
            print(f"  {filepath}")
            print(f"    可能硬编码文本: {', '.join(strings)}")

if __name__ == "__main__":
    print("🔍 翻译问题诊断")
    print("=" * 60)
    
    find_hardcoded_english()
    check_html_templates()
    check_translation_coverage()
    check_t_function_usage()
    
    print("\n" + "=" * 60)
    print("诊断完成！")