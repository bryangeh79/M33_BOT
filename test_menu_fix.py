#!/usr/bin/env python3
"""
测试菜单修复
"""

import re

def check_t_function_calls():
    """检查t()函数调用"""
    print("=== 检查t()函数调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找错误的t()调用：t("KEY", param, lang=...) 其中param不是命名参数
    # 正确的：t("KEY", lang=param) 或 t("KEY", key=value, lang=...)
    # 错误的：t("KEY", param, lang=...)
    pattern = r't\(("[^"]+"|\'[^\']+\'),\s*([^=,)]+),\s*lang='
    errors = re.findall(pattern, content)
    
    if errors:
        print(f"❌ 找到 {len(errors)} 个错误的t()调用:")
        for key, param in errors[:5]:
            print(f"  t({key}, {param}, lang=...)")
        return False
    else:
        print("✅ 没有错误的t()调用")
        return True

def check_get_calls():
    """检查.get()调用"""
    print("\n=== 检查.get()调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找错误的.get()调用：.get("key", default, lang=...)
    pattern = r'\.get\(("[^"]+"|\'[^\']+\'),\s*([^,)]+),\s*lang=_get_user_lang'
    errors = re.findall(pattern, content)
    
    if errors:
        print(f"❌ 找到 {len(errors)} 个错误的.get()调用:")
        for key, default in errors[:5]:
            print(f"  .get({key}, {default}, lang=_get_user_lang(...))")
        return False
    else:
        print("✅ 没有错误的.get()调用")
        return True

def check_split_calls():
    """检查.split()调用"""
    print("\n=== 检查.split()调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找错误的.split()调用：.split("/", lang=...)
    pattern = r'\.split\(("[^"]+"|\'[^\']+\'),\s*lang=_get_user_lang'
    errors = re.findall(pattern, content)
    
    if errors:
        print(f"❌ 找到 {len(errors)} 个错误的.split()调用:")
        for sep in errors[:5]:
            print(f"  .split({sep}, lang=_get_user_lang(...))")
        return False
    else:
        print("✅ 没有错误的.split()调用")
        return True

def main():
    print("🔍 测试菜单修复")
    print("=" * 60)
    
    tests = [
        check_t_function_calls,
        check_get_calls,
        check_split_calls,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！菜单应该可以正常工作了。")
        print("\n问题应该是修复了：")
        print("1. 错误的t()调用: t(\"KEY\", param, lang=...) → t(\"KEY\", lang=param)")
        print("2. 错误的.get()调用")
        print("3. 错误的.split()调用")
        return True
    else:
        print("⚠️ 有些测试未通过，需要进一步修复。")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)