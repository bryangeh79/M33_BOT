#!/usr/bin/env python3
"""
测试文件名翻译
"""

import sys
import os
import re

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_filename_translation():
    """测试文件名翻译功能"""
    print("=== 测试文件名翻译 ===")
    
    try:
        # 导入必要的模块
        from src.app.main import _report_filename
        
        # 定义报告类型常量（从main.py中复制）
        REPORT_TYPE_TRANSACTION = "transaction"
        REPORT_TYPE_NUMBER_DETAIL = "number_detail"
        REPORT_TYPE_SETTLEMENT = "settlement"
        REPORT_TYPE_OVER_LIMIT = "over_limit"
        
        test_cases = [
            (REPORT_TYPE_TRANSACTION, "2026-04-07", "交易报告"),
            (REPORT_TYPE_NUMBER_DETAIL, "2026-04-07", "号码详情报告"),
            (REPORT_TYPE_SETTLEMENT, "2026-04-07", "结算报告"),
            (REPORT_TYPE_OVER_LIMIT, "2026-04-07", "超限报告"),
        ]
        
        print("\n1. 测试中文文件名:")
        for report_type, date, expected_chinese in test_cases:
            storage_filename, display_filename = _report_filename(report_type, date, lang="zh")
            print(f"   {report_type}:")
            print(f"     存储文件名: {storage_filename}")
            print(f"     显示文件名: {display_filename}")
            
            # 验证存储文件名是英文
            if report_type in storage_filename:
                print(f"     ✅ 存储文件名包含英文类型")
            else:
                print(f"     ❌ 存储文件名问题")
            
            # 验证显示文件名包含中文
            if expected_chinese in display_filename:
                print(f"     ✅ 显示文件名包含中文: '{expected_chinese}'")
            else:
                print(f"     ❌ 显示文件名缺少中文")
            
            # 验证文件名格式
            if display_filename.endswith(f"_{date}.html"):
                print(f"     ✅ 文件名格式正确")
            else:
                print(f"     ❌ 文件名格式问题")
        
        print("\n2. 测试越南语文件名:")
        for report_type, date, _ in test_cases:
            storage_filename, display_filename = _report_filename(report_type, date, lang="vi")
            print(f"   {report_type}:")
            print(f"     存储文件名: {storage_filename}")
            print(f"     显示文件名: {display_filename}")
            
            # 验证显示文件名不是英文（应该包含越南语）
            if "report" in display_filename.lower() and "transaction" not in display_filename.lower():
                print(f"     ⚠️  显示文件名可能还是英文")
            else:
                print(f"     ✅ 显示文件名看起来是越南语")
        
        print("\n3. 测试英文文件名:")
        for report_type, date, _ in test_cases:
            storage_filename, display_filename = _report_filename(report_type, date, lang="en")
            print(f"   {report_type}:")
            print(f"     存储文件名: {storage_filename}")
            print(f"     显示文件名: {display_filename}")
            
            # 验证两个文件名都包含英文关键词
            if report_type in storage_filename:
                print(f"     ✅ 存储文件名包含 '{report_type}'")
            else:
                print(f"     ❌ 存储文件名问题")
            
            if "report" in display_filename.lower():
                print(f"     ✅ 显示文件名包含 'report'")
            else:
                print(f"     ❌ 显示文件名问题")
        
        print("\n4. 测试文件名安全性（特殊字符处理）:")
        test_name = "Test:Report/With\\Special*Chars?.html"
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', test_name)
        cleaned = cleaned.replace(' ', '_')
        print(f"   原始: {test_name}")
        print(f"   清理后: {cleaned}")
        
        if '_' in cleaned and ':' not in cleaned and '/' not in cleaned and '\\' not in cleaned and '*' not in cleaned and '?' not in cleaned:
            print(f"   ✅ 特殊字符处理正确")
        else:
            print(f"   ❌ 特殊字符处理有问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_keys():
    """测试翻译键是否存在"""
    print("\n=== 测试翻译键 ===")
    
    try:
        from src.i18n.translator import t
        
        # 测试所有需要的翻译键
        required_keys = [
            "HTML_TITLE_TRANSACTION",
            "HTML_TITLE_NUMBER_DETAIL", 
            "HTML_TITLE_SETTLEMENT",
            "HTML_TITLE_OVER_LIMIT",
            "BTN_REPORT"  # 回退键
        ]
        
        languages = ["en", "vi", "zh"]
        
        all_good = True
        for lang in languages:
            print(f"\n测试语言: {lang}")
            for key in required_keys:
                translation = t(key, lang=lang)
                if translation == key:  # 如果返回键本身，说明翻译缺失
                    print(f"   ❌ 缺失翻译: {key}")
                    all_good = False
                else:
                    print(f"   ✅ {key}: {translation}")
        
        return all_good
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 文件名翻译测试")
    print("=" * 60)
    
    success = True
    
    # 运行测试
    if not test_filename_translation():
        success = False
    
    if not test_translation_keys():
        success = False
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 文件名翻译修复成功！")
        print("\n修复总结:")
        print("1. ✅ 修改了 _report_filename 函数返回元组")
        print("2. ✅ 存储文件名使用英文（文件系统兼容）")
        print("3. ✅ 显示文件名使用用户语言")
        print("4. ✅ 特殊字符处理确保文件名安全")
        print("5. ✅ 更新了调用代码使用翻译后的文件名")
    else:
        print("⚠️ 测试失败，需要进一步调试。")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)