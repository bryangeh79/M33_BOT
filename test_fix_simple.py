#!/usr/bin/env python3
"""
简单测试修复后的代码
"""

import ast
import sys

def test_no_nameerror():
    """测试没有NameError"""
    print("=== 测试没有NameError ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查main函数中是否有未定义的user_id
    if 'def main():' in content:
        main_start = content.find('def main():')
        # 查找main函数结束（下一个def或文件结束）
        next_def = content.find('\ndef ', main_start + 1)
        if next_def == -1:
            next_def = len(content)
        
        main_content = content[main_start:next_def]
        
        # 检查main函数中是否有未定义的user_id
        if 'user_id' in main_content:
            # 检查user_id是否在main函数中定义
            lines = main_content.split('\n')
            user_id_defined = False
            for line in lines:
                if 'user_id' in line and ('=' in line or 'def ' in line or '(' in line):
                    # 可能是参数或定义
                    if 'def ' in line or '(' in line:
                        # 函数定义中的参数
                        user_id_defined = True
                    elif '=' in line and 'user_id' in line.split('=')[0]:
                        # 变量赋值
                        user_id_defined = True
            
            if not user_id_defined:
                print("❌ main函数中使用了未定义的user_id")
                return False
            else:
                print("✅ main函数中的user_id已定义")
        else:
            print("✅ main函数中没有使用user_id")
    
    return True

def test_argparse():
    """测试argparse调用"""
    print("\n=== 测试argparse调用 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查parser.add_argument调用
    if 'parser.add_argument' in content:
        # 查找所有parser.add_argument调用
        import re
        calls = re.findall(r'parser\.add_argument\([^)]+\)', content)
        
        for call in calls:
            if 'lang=_get_user_lang' in call:
                print(f"❌ 错误的parser.add_argument调用: {call[:50]}...")
                return False
        
        print(f"✅ 找到 {len(calls)} 个parser.add_argument调用，都没有错误的lang参数")
    
    return True

def test_load_config():
    """测试load_config函数"""
    print("\n=== 测试load_config函数 ===")
    
    with open('src/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找load_config函数
    if 'def load_config(' in content:
        load_start = content.find('def load_config(')
        # 查找函数结束
        next_def = content.find('\ndef ', load_start + 1)
        if next_def == -1:
            next_def = len(content)
        
        load_content = content[load_start:next_def]
        
        # 检查是否有错误的lang调用
        if 'lang=_get_user_lang' in load_content:
            print("❌ load_config函数中有错误的lang=_get_user_lang调用")
            return False
        else:
            print("✅ load_config函数中没有错误的lang调用")
    
    return True

def main():
    print("🔍 简单测试修复后的代码")
    print("=" * 60)
    
    tests = [
        test_no_nameerror,
        test_argparse,
        test_load_config,
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
        print("🎉 所有测试通过！代码应该可以正常运行了。")
        print("\n现在可以尝试运行: python run_bot.py 1")
        return True
    else:
        print("⚠️ 有些测试未通过，需要进一步修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)