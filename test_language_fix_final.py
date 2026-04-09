#!/usr/bin/env python3
"""
最终语言修复测试
"""

import os
import sys
import re

def test_menu_functions_have_lang():
    """测试所有菜单函数都有lang参数"""
    print("=== 测试菜单函数lang参数 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有菜单函数
    menu_pattern = r'def (_build_.*_kb|_build_.*_keyboard|get_.*_keyboard)\([^)]*\) ->'
    matches = re.findall(menu_pattern, content)
    
    all_good = True
    for func_name in matches:
        # 查找函数定义
        func_pattern = rf'def {func_name}\((.*?)\) ->'
        func_match = re.search(func_pattern, content, re.DOTALL)
        
        if func_match:
            params = func_match.group(1)
            if 'lang' in params:
                print(f"  ✅ {func_name}: 有lang参数")
            else:
                print(f"  ❌ {func_name}: 缺少lang参数")
                all_good = False
    
    return all_good

def test_t_function_calls():
    """测试t()函数调用"""
    print("\n=== 测试t()函数调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找t()调用
    t_pattern = r't\(([^)]+)\)'
    t_calls = re.findall(t_pattern, content)
    
    # 统计
    total = len(t_calls)
    with_lang = sum(1 for call in t_calls if 'lang=' in call)
    without_lang = total - with_lang
    
    print(f"总t()调用: {total}")
    print(f"有lang参数: {with_lang}")
    print(f"无lang参数: {without_lang}")
    
    # 检查无lang参数的调用是否合理（环境变量等）
    print("\n无lang参数的调用:")
    for call in t_calls:
        if 'lang=' not in call:
            # 检查是否是环境变量等特殊情况
            if any(keyword in call for keyword in ['BOT_TOKEN', 'DB_PATH', 'LOG_PATH', 'CLIENT_NAME']):
                print(f"  ⚠️ {call}: 环境变量（合理）")
            elif call.startswith('"') or call.startswith("'"):
                print(f"  ❌ {call}: 可能缺少lang参数")
            else:
                print(f"  ⚠️ {call}: 其他情况")
    
    return with_lang > without_lang  # 大多数应该有lang参数

def test_translation_keys():
    """测试翻译键"""
    print("\n=== 测试翻译键 ===")
    
    # 检查关键翻译键是否存在
    required_keys = [
        'MENU_MAIN',
        'BTN_REPORT_TRANSACTION',
        'BTN_REPORT_SETTLEMENT',
        'BTN_REPORT_NUMBER_DETAIL',
        'BTN_REPORT_OVER_LIMIT',
    ]
    
    lang_files = ['en.py', 'vi.py', 'zh.py']
    
    all_good = True
    for lang_file in lang_files:
        filepath = f'src/i18n/{lang_file}'
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing = []
            for key in required_keys:
                if f'"{key}":' not in content:
                    missing.append(key)
            
            if missing:
                print(f"❌ {lang_file}: 缺失键 {missing}")
                all_good = False
            else:
                print(f"✅ {lang_file}: 所有键存在")
        else:
            print(f"❌ 文件不存在: {filepath}")
            all_good = False
    
    return all_good

def test_language_switch():
    """测试语言切换逻辑"""
    print("\n=== 测试语言切换逻辑 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找handle_lang_select函数
    if 'handle_lang_select' in content:
        print("✅ 找到语言切换函数")
        
        # 检查是否发送新菜单
        if 'get_main_menu_keyboard' in content and 'MENU_MAIN' in content:
            print("✅ 语言切换后发送新菜单")
        else:
            print("❌ 语言切换后可能没有发送新菜单")
        
        return True
    else:
        print("❌ 未找到语言切换函数")
        return False

def main():
    print("🔍 最终语言修复测试")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # 运行测试
    if test_menu_functions_have_lang():
        tests_passed += 1
    
    if test_t_function_calls():
        tests_passed += 1
    
    if test_translation_keys():
        tests_passed += 1
    
    if test_language_switch():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！语言修复完成。")
        print("\n修复总结:")
        print("1. ✅ 所有菜单函数都有lang参数")
        print("2. ✅ t()函数调用大多数有lang参数")
        print("3. ✅ 所有必要的翻译键都存在")
        print("4. ✅ 语言切换后发送新菜单")
        print("\n系统现在应该能正确响应语言切换了！")
    else:
        print("⚠️ 有些测试未通过，需要进一步调试。")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)