#!/usr/bin/env python3
"""
系统性检查语言一致性
检查所有可能受语言切换影响的界面元素
"""

import os
import sys
import re

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_menu_functions():
    """检查所有菜单函数是否支持多语言"""
    print("=== 检查菜单函数语言支持 ===")
    
    menu_functions = []
    
    # 检查main.py中的菜单函数
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 查找菜单构建函数
    menu_patterns = [
        r'def _build_.*_kb\(.*\) -> ReplyKeyboardMarkup:',
        r'def _build_.*_keyboard\(.*\) -> InlineKeyboardMarkup:',
        r'def get_.*_keyboard\(.*\):',
    ]
    
    for pattern in menu_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            menu_functions.append(match)
    
    print(f"找到 {len(menu_functions)} 个菜单函数:")
    for func in menu_functions[:10]:  # 显示前10个
        print(f"  {func}")
    
    # 检查这些函数是否有lang参数
    print("\n检查函数是否有lang参数:")
    for func_decl in menu_functions:
        # 提取函数名
        func_name = func_decl.split('def ')[1].split('(')[0]
        
        # 查找函数定义
        func_pattern = rf'def {func_name}\(.*?\):'
        func_match = re.search(func_pattern, content, re.DOTALL)
        
        if func_match:
            func_def = func_match.group(0)
            if 'lang' in func_def:
                print(f"  ✅ {func_name}: 有lang参数")
            else:
                print(f"  ❌ {func_name}: 缺少lang参数")
    
    return menu_functions

def check_hardcoded_text():
    """检查硬编码的文本"""
    print("\n=== 检查硬编码文本 ===")
    
    # 常见硬编码的英文文本
    hardcoded_patterns = [
        r'"MN"', r'"MT"', r'"MB"',
        r'"Today"', r'"Back"', r'"Close"',
        r'"Date:"', r'"Total:"', r'"Region:"',
        r'"Transaction"', r'"Settlement"',
        r'"Number Detail"', r'"Over Limit"',
    ]
    
    files_to_check = [
        'src/app/main.py',
        'src/bot/menus/bet_menu.py',
        'src/bot/menus/main_menu.py',
    ]
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n检查文件: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_hardcoded = []
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    found_hardcoded.extend(matches)
            
            if found_hardcoded:
                print(f"  发现硬编码文本: {set(found_hardcoded)}")
            else:
                print("  ✅ 未发现硬编码文本")

def check_t_function_usage():
    """检查t()函数使用情况"""
    print("\n=== 检查t()函数使用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计t()调用
    t_calls = re.findall(r't\([^)]+\)', content)
    print(f"t()函数调用次数: {len(t_calls)}")
    
    # 检查是否都传递了lang参数
    t_with_lang = 0
    t_without_lang = 0
    
    for call in t_calls[:20]:  # 检查前20个
        if 'lang=' in call:
            t_with_lang += 1
        else:
            t_without_lang += 1
    
    print(f"  有lang参数: {t_with_lang}")
    print(f"  无lang参数: {t_without_lang}")
    
    if t_without_lang > 0:
        print("  ⚠️ 有些t()调用没有传递lang参数")
        # 显示示例
        print("  示例无lang调用:")
        for call in t_calls[:5]:
            if 'lang=' not in call:
                print(f"    {call}")

def check_translation_keys():
    """检查翻译键覆盖"""
    print("\n=== 检查翻译键覆盖 ===")
    
    # 从en.py提取所有翻译键
    en_file = 'src/i18n/en.py'
    if os.path.exists(en_file):
        with open(en_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取STRINGS字典中的键
        import ast
        try:
            tree = ast.parse(content)
            en_keys = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    for key_node, value_node in zip(node.keys, node.values):
                        if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                            en_keys.add(key_node.value)
            
            print(f"英文翻译键总数: {len(en_keys)}")
            
            # 检查其他语言文件
            lang_files = ['vi.py', 'zh.py']
            for lang_file in lang_files:
                filepath = f'src/i18n/{lang_file}'
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lang_content = f.read()
                    
                    lang_tree = ast.parse(lang_content)
                    lang_keys = set()
                    
                    for node in ast.walk(lang_tree):
                        if isinstance(node, ast.Dict):
                            for key_node, value_node in zip(node.keys, node.values):
                                if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                                    lang_keys.add(key_node.value)
                    
                    missing = en_keys - lang_keys
                    print(f"{lang_file}: {len(lang_keys)}键, 缺失{len(missing)}键")
                    
                    if missing:
                        print(f"  示例缺失键: {list(missing)[:5]}")
                else:
                    print(f"❌ 文件不存在: {filepath}")
        
        except Exception as e:
            print(f"解析错误: {e}")

def check_language_refresh_mechanism():
    """检查语言刷新机制"""
    print("\n=== 检查语言刷新机制 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查语言切换后是否有刷新菜单的逻辑
    if 'handle_language_set' in content:
        print("找到语言切换处理函数: handle_language_set")
        
        # 查找这个函数
        pattern = r'async def handle_language_set\(.*?\) -> None:.*?(?=\nasync def|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            func_content = match.group(0)
            print("函数内容摘要:")
            lines = func_content.split('\n')
            for line in lines[:10]:
                if line.strip():
                    print(f"  {line}")
            
            # 检查是否有刷新其他界面的逻辑
            if 'edit_message_reply_markup' in func_content or 'send_message' in func_content:
                print("✅ 语言切换后有界面刷新")
            else:
                print("❌ 语言切换后没有刷新其他界面")
        else:
            print("❌ 无法提取函数内容")
    else:
        print("❌ 未找到语言切换处理函数")

def main():
    print("🔍 系统性语言一致性检查")
    print("=" * 60)
    
    # 运行检查
    check_menu_functions()
    check_hardcoded_text()
    check_t_function_usage()
    check_translation_keys()
    check_language_refresh_mechanism()
    
    print("\n" + "=" * 60)
    print("检查完成！")
    print("\n主要发现:")
    print("1. 菜单函数需要统一添加lang参数")
    print("2. 需要检查硬编码文本")
    print("3. t()函数调用需要统一传递lang参数")
    print("4. 语言切换后需要刷新所有打开的菜单")
    
    return True

if __name__ == "__main__":
    main()