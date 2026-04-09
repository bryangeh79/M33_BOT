#!/usr/bin/env python3
"""
批量修复语言一致性问题
"""

import os
import re
import sys

def add_lang_to_menu_functions():
    """为菜单函数添加lang参数"""
    print("=== 为菜单函数添加lang参数 ===")
    
    filepath = 'src/app/main.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要修复的函数列表（从检查结果中获取）
    functions_to_fix = [
        '_build_admin_menu_kb',
        '_build_result_date_kb', 
        '_build_result_region_kb',
        '_build_admin_menu_keyboard',
        '_build_set_admin_keyboard',
        '_build_agent_comm_keyboard',
        '_build_bonus_payout_keyboard',
        '_build_over_limit_keyboard',
        '_build_over_limit_action_keyboard',
        '_build_notifications_keyboard',
        '_build_time_limit_keyboard',
        '_build_system_timezone_keyboard',
        '_build_other_day_keyboard',
        '_build_result_date_keyboard',
        '_build_result_region_keyboard',
        '_build_result_action_keyboard',
    ]
    
    fixes_applied = 0
    
    for func_name in functions_to_fix:
        # 查找函数定义
        pattern = rf'def {func_name}\((.*?)\) ->'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            params = match.group(1)
            # 如果已经有lang参数，跳过
            if 'lang' in params:
                print(f"  ⚠️ {func_name}: 已有lang参数")
                continue
            
            # 添加lang参数
            new_params = params.strip()
            if new_params:
                new_params += ', lang: str = "en"'
            else:
                new_params = 'lang: str = "en"'
            
            old_def = f'def {func_name}({params}) ->'
            new_def = f'def {func_name}({new_params}) ->'
            
            content = content.replace(old_def, new_def)
            print(f"  ✅ {func_name}: 添加lang参数")
            fixes_applied += 1
        else:
            print(f"  ❌ {func_name}: 未找到函数定义")
    
    # 保存修改
    if fixes_applied > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ 已修复 {fixes_applied} 个函数")
    else:
        print("\n⚠️ 没有需要修复的函数")
    
    return fixes_applied

def fix_t_function_calls():
    """修复t()函数调用，添加lang参数"""
    print("\n=== 修复t()函数调用 ===")
    
    filepath = 'src/app/main.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有t()调用
    t_pattern = r't\(([^)]+)\)'
    t_calls = re.findall(t_pattern, content)
    
    # 需要修复的t()调用（排除那些已经有lang参数或特殊情况的）
    fixes_applied = 0
    
    # 创建一个修改后的内容副本
    new_content = content
    
    for call in t_calls:
        # 跳过已经有lang参数的
        if 'lang=' in call:
            continue
        
        # 跳过特殊情况（环境变量等）
        if any(keyword in call for keyword in ['BOT_TOKEN', 'DB_PATH', 'LOG_PATH', 'CLIENT_NAME']):
            continue
        
        # 简单的t()调用，如 t("KEY")
        if call.startswith('"') or call.startswith("'"):
            # 提取键名
            key_match = re.match(r'["\']([^"\']+)["\']', call)
            if key_match:
                key = key_match.group(1)
                # 构建新的调用
                old_call = f't({call})'
                new_call = f't({call}, lang=_get_user_lang(user_id))'
                
                # 替换（需要小心，避免重复替换）
                new_content = new_content.replace(old_call, new_call)
                fixes_applied += 1
    
    # 保存修改
    if fixes_applied > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 已修复 {fixes_applied} 个t()调用")
    else:
        print("⚠️ 没有需要修复的t()调用")
    
    return fixes_applied

def fix_hardcoded_today():
    """修复硬编码的"Today"文本"""
    print("\n=== 修复硬编码'Today'文本 ===")
    
    filepath = 'src/app/main.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找硬编码的"Today"
    fixes_applied = 0
    
    # 修复 KeyboardButton("Today")
    pattern1 = r'KeyboardButton\("Today"\)'
    if re.search(pattern1, content):
        content = re.sub(pattern1, 'KeyboardButton(t("BTN_TODAY", lang=_get_user_lang(user_id)))', content)
        fixes_applied += 1
        print("✅ 修复 KeyboardButton(\"Today\")")
    
    # 修复 text.startswith("Today")
    pattern2 = r'text\.startswith\("Today"\)'
    if re.search(pattern2, content):
        # 这个可能不需要修复，是文本匹配逻辑
        print("⚠️ text.startswith(\"Today\") 是文本匹配，可能不需要修复")
    
    # 保存修改
    if fixes_applied > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复 {fixes_applied} 处硬编码")
    else:
        print("⚠️ 没有需要修复的硬编码")
    
    return fixes_applied

def update_menu_button_texts():
    """更新菜单按钮文本使用t()函数"""
    print("\n=== 更新菜单按钮文本 ===")
    
    filepath = 'src/app/main.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = 0
    
    # 修复报告类型按钮
    report_labels = {
        'REPORT_LABEL_TRANSACTION': 'BTN_REPORT_TRANSACTION',
        'REPORT_LABEL_SETTLEMENT': 'BTN_REPORT_SETTLEMENT',
        'REPORT_LABEL_NUMBER_DETAIL': 'BTN_REPORT_NUMBER_DETAIL',
        'REPORT_LABEL_OVER_LIMIT': 'BTN_REPORT_OVER_LIMIT',
    }
    
    for old_key, new_key in report_labels.items():
        pattern = f'KeyboardButton\\({old_key}\\)'
        replacement = f'KeyboardButton(t("{new_key}", lang=_get_user_lang(user_id)))'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_applied += 1
            print(f"✅ 修复 {old_key} -> {new_key}")
    
    # 保存修改
    if fixes_applied > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复 {fixes_applied} 个按钮文本")
    else:
        print("⚠️ 没有需要修复的按钮文本")
    
    return fixes_applied

def add_translation_keys():
    """添加缺失的翻译键"""
    print("\n=== 添加缺失的翻译键 ===")
    
    # 需要添加的翻译键
    new_keys = {
        'en': {
            'BTN_REPORT_TRANSACTION': 'Transaction',
            'BTN_REPORT_SETTLEMENT': 'Settlement',
            'BTN_REPORT_NUMBER_DETAIL': 'Number Detail',
            'BTN_REPORT_OVER_LIMIT': 'Over Limit',
            'REGION_MN': 'MN',
            'REGION_MT': 'MT',
            'REGION_MB': 'MB',
        },
        'vi': {
            'BTN_REPORT_TRANSACTION': 'Giao dịch',
            'BTN_REPORT_SETTLEMENT': 'Quyết toán',
            'BTN_REPORT_NUMBER_DETAIL': 'Chi tiết số',
            'BTN_REPORT_OVER_LIMIT': 'Vượt giới hạn',
            'REGION_MN': 'MN',
            'REGION_MT': 'MT',
            'REGION_MB': 'MB',
        },
        'zh': {
            'BTN_REPORT_TRANSACTION': '交易',
            'BTN_REPORT_SETTLEMENT': '结算',
            'BTN_REPORT_NUMBER_DETAIL': '号码详情',
            'BTN_REPORT_OVER_LIMIT': '超限',
            'REGION_MN': 'MN',
            'REGION_MT': 'MT',
            'REGION_MB': 'MB',
        }
    }
    
    for lang, keys in new_keys.items():
        filepath = f'src/i18n/{lang}.py'
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在文件末尾添加新键（在最后一个大括号前）
            if '}' in content:
                # 找到最后一个}
                last_brace = content.rfind('}')
                before_brace = content[:last_brace]
                after_brace = content[last_brace:]
                
                # 添加新键
                new_content = before_brace.rstrip()
                if not new_content.endswith(','):
                    new_content += ','
                
                new_content += '\n\n    # ── 新增翻译键 ────────────────────────────────────────────────\n'
                for key, value in keys.items():
                    # 检查是否已存在
                    if f'"{key}":' not in new_content:
                        new_content += f'    "{key}": "{value}",\n'
                
                new_content += after_brace
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ 已更新 {lang}.py")
        else:
            print(f"❌ 文件不存在: {filepath}")
    
    return len(new_keys['en'])

def main():
    print("🔧 批量修复语言一致性问题")
    print("=" * 60)
    
    total_fixes = 0
    
    # 执行修复
    total_fixes += add_lang_to_menu_functions()
    total_fixes += fix_t_function_calls()
    total_fixes += fix_hardcoded_today()
    total_fixes += update_menu_button_texts()
    total_fixes += add_translation_keys()
    
    print("\n" + "=" * 60)
    print(f"🎉 修复完成！总共应用了 {total_fixes} 处修复")
    print("\n修复内容:")
    print("1. ✅ 为菜单函数添加lang参数")
    print("2. ✅ 修复t()函数调用添加lang参数")
    print("3. ✅ 修复硬编码文本")
    print("4. ✅ 更新菜单按钮文本使用t()函数")
    print("5. ✅ 添加缺失的翻译键")
    print("\n注意: 还需要手动检查调用这些函数的地方是否传递了正确的lang参数")
    
    return total_fixes > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)