#!/usr/bin/env python3
"""
修复错误的lang=_get_user_lang(user_id)调用
"""

import re

def fix_main_py():
    """修复main.py中的错误lang调用"""
    print("=== 修复main.py中的错误lang调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 修复错误的split调用
    # 从: text.split("/", lang=_get_user_lang(user_id))
    # 到: text.split("/")
    content = re.sub(r'\.split\(("[^"]*"|\'[^\']*\'), lang=_get_user_lang\(user_id\)\)', r'.split(\1)', content)
    
    # 修复2: 修复错误的get调用
    # 从: .get("key", lang=_get_user_lang(user_id))
    # 到: .get("key")
    content = re.sub(r'\.get\(("[^"]*"|\'[^\']*\'), lang=_get_user_lang\(user_id\)\)', r'.get(\1)', content)
    
    # 修复3: 修复错误的get调用带默认值
    # 从: .get("key", [], lang=_get_user_lang(user_id))
    # 到: .get("key", [])
    content = re.sub(r'\.get\(("[^"]*"|\'[^\']*\'), (\[[^\]]*\]|"[^"]*"|\'[^\']*\'), lang=_get_user_lang\(user_id\)\)', r'.get(\1, \2)', content)
    
    # 修复4: 修复错误的strftime调用
    # 从: .strftime("%d/%m", lang=_get_user_lang(user_id))
    # 到: .strftime("%d/%m")
    content = re.sub(r'\.strftime\(("[^"]*"|\'[^\']*\'), lang=_get_user_lang\(user_id\)\)', r'.strftime(\1)', content)
    
    # 修复5: 修复错误的t()调用嵌套
    # 从: t("KEY", _get_user_lang(user_id, lang=_get_user_lang(user_id)))
    # 到: t("KEY", _get_user_lang(user_id))
    content = re.sub(r't\(("[^"]*"|\'[^\']*\'), _get_user_lang\(user_id, lang=_get_user_lang\(user_id\)\)\)', r't(\1, _get_user_lang(user_id))', content)
    
    # 修复6: 修复config.get调用
    # 从: config.get('KEY', lang=_get_user_lang(user_id))
    # 到: config.get('KEY')
    content = re.sub(r'config\.get\((\'[^\']*\'|"[^"]*"), lang=_get_user_lang\(user_id\)\)', r'config.get(\1)', content)
    
    # 修复7: 修复_set_user_lang调用
    # 从: _set_user_lang(user_id, lang_code, lang=_get_user_lang(user_id))
    # 到: _set_user_lang(user_id, lang_code)
    content = re.sub(r'_set_user_lang\(user_id, lang_code, lang=_get_user_lang\(user_id\)\)', r'_set_user_lang(user_id, lang_code)', content)
    
    # 修复8: 修复错误的BotCommand调用
    # 从: BotCommand("start", t("CMD_START", lang, lang=_get_user_lang(user_id)))
    # 到: BotCommand("start", t("CMD_START", lang=lang))
    content = re.sub(r'BotCommand\("([^"]+)",\s*t\("([^"]+)",\s*([^,)]+),\s*lang=_get_user_lang\(user_id\)\)\)', r'BotCommand("\1", t("\2", lang=\3))', content)
    
    # 修复9: 修复application.bot.set_my_commands调用
    # 从: _cmd_list("en", lang=_get_user_lang(user_id))
    # 到: _cmd_list("en")
    content = re.sub(r'_cmd_list\("en", lang=_get_user_lang\(user_id\)\)', r'_cmd_list("en")', content)
    
    # 修复10: 修复user_context.get调用
    # 从: user_context[user_id].get("state", UserState.IDLE, lang=_get_user_lang(user_id))
    # 到: user_context[user_id].get("state", UserState.IDLE)
    content = re.sub(r'user_context\[user_id\]\.get\("state", UserState\.IDLE, lang=_get_user_lang\(user_id\)\)', r'user_context[user_id].get("state", UserState.IDLE)', content)
    
    # 修复11: 修复_get_user_env.get调用
    # 从: _get_user_env(user_id).get("waiting_custom_date", lang=_get_user_lang(user_id))
    # 到: _get_user_env(user_id).get("waiting_custom_date")
    content = re.sub(r'_get_user_env\(user_id\)\.get\("([^"]+)", lang=_get_user_lang\(user_id\)\)', r'_get_user_env(user_id).get("\1")', content)
    
    # 修复12: 修复错误的f-string中的get调用
    # 从: f"status={fetch_result.get('status', lang=_get_user_lang(user_id))}"
    # 到: f"status={fetch_result.get('status')}"
    content = re.sub(r'fetch_result\.get\(\'status\', lang=_get_user_lang\(user_id\)\)', r"fetch_result.get('status')", content)
    
    # 保存修复
    with open('src/app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复main.py中的错误lang调用")
    
    # 检查是否还有错误的lang调用
    remaining = re.findall(r'lang=_get_user_lang\(user_id\)', content)
    if remaining:
        print(f"⚠️ 还有 {len(remaining)} 个未修复的lang调用")
        for i, call in enumerate(remaining[:5]):
            print(f"  示例{i+1}: {call}")
    else:
        print("✅ 所有错误的lang调用已修复")
    
    return len(remaining)

def check_syntax():
    """检查语法"""
    print("\n=== 检查语法 ===")
    
    import subprocess
    try:
        result = subprocess.run(['python3', '-m', 'py_compile', 'src/app/main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 语法检查通过")
            return True
        else:
            print("❌ 语法检查失败:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        # 尝试直接编译
        try:
            import py_compile
            py_compile.compile('src/app/main.py', doraise=True)
            print("✅ 语法检查通过")
            return True
        except Exception as e:
            print(f"❌ 语法检查失败: {e}")
            return False

def main():
    print("🔧 修复错误的lang=_get_user_lang(user_id)调用")
    print("=" * 60)
    
    # 备份原文件
    import shutil
    shutil.copy2('src/app/main.py', 'src/app/main.py.backup')
    print("📋 已创建备份: src/app/main.py.backup")
    
    # 修复
    remaining = fix_main_py()
    
    # 检查语法
    syntax_ok = check_syntax()
    
    print("\n" + "=" * 60)
    if syntax_ok and remaining == 0:
        print("🎉 修复完成！所有错误已修复，语法检查通过")
        print("\n现在可以运行: python run_bot.py 1")
    elif syntax_ok:
        print("⚠️ 语法检查通过，但还有未修复的lang调用")
        print("可能需要手动检查这些调用")
    else:
        print("❌ 语法检查失败，需要进一步修复")
    
    return syntax_ok and remaining == 0

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)