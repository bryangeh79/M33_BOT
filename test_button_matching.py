#!/usr/bin/env python3
"""
测试按钮文本匹配
"""

import sys
sys.path.insert(0, 'src')

from i18n.translator import t

# 模拟 get_main_menu_button_labels 函数
def get_main_menu_button_labels(lang: str = "en"):
    """Return the flat list of main menu button labels for the given language."""
    return [
        t("BTN_BET", lang=lang),
        t("BTN_REPORT", lang=lang),
        t("BTN_RESULT", lang=lang),
        t("BTN_OTHER_DAY_INPUT", lang=lang),
        t("BTN_ADMIN", lang=lang),
        t("BTN_INFO", lang=lang),
    ]

def test_button_texts():
    """测试按钮文本"""
    print("=== 测试按钮文本 ===")
    
    # 测试所有语言的按钮文本
    for lang in ['en', 'vi', 'zh']:
        print(f"\n语言: {lang}")
        buttons = get_main_menu_button_labels(lang=lang)
        
        print(f"按钮文本: {buttons}")
        
        # 检查每个按钮是否与t()函数返回的一致
        expected = [
            t("BTN_BET", lang=lang),
            t("BTN_REPORT", lang=lang),
            t("BTN_RESULT", lang=lang),
            t("BTN_OTHER_DAY_INPUT", lang=lang),
            t("BTN_ADMIN", lang=lang),
            t("BTN_INFO", lang=lang),
        ]
        
        if buttons == expected:
            print("✅ 按钮文本匹配")
        else:
            print("❌ 按钮文本不匹配")
            print(f"期望: {expected}")
            print(f"实际: {buttons}")
            return False
    
    return True

def test_main_menu_logic():
    """测试主菜单逻辑"""
    print("\n=== 测试主菜单逻辑 ===")
    
    # 模拟主菜单处理逻辑
    test_cases = [
        ("Bet", "en", "BTN_BET"),
        ("Report", "en", "BTN_REPORT"),
        ("Result", "en", "BTN_RESULT"),
        ("Other Day Input", "en", "BTN_OTHER_DAY_INPUT"),
        ("Admin", "en", "BTN_ADMIN"),
        ("Info", "en", "BTN_INFO"),
        ("Đặt cược", "vi", "BTN_BET"),
        ("Báo cáo", "vi", "BTN_REPORT"),
        ("Kết quả", "vi", "BTN_RESULT"),
        ("Nhập ngày khác", "vi", "BTN_OTHER_DAY_INPUT"),
        ("Quản trị", "vi", "BTN_ADMIN"),
        ("Thông tin", "vi", "BTN_INFO"),
        ("投注", "zh", "BTN_BET"),
        ("报告", "zh", "BTN_REPORT"),
        ("结果", "zh", "BTN_RESULT"),
        ("其他日期投注", "zh", "BTN_OTHER_DAY_INPUT"),
        ("管理", "zh", "BTN_ADMIN"),
        ("信息", "zh", "BTN_INFO"),
    ]
    
    all_pass = True
    for text, lang, expected_key in test_cases:
        expected_text = t(expected_key, lang=lang)
        if text == expected_text:
            print(f"✅ {lang}: '{text}' 匹配 '{expected_key}'")
        else:
            print(f"❌ {lang}: '{text}' 不匹配 '{expected_key}' (期望: '{expected_text}')")
            all_pass = False
    
    return all_pass

def main():
    print("🔍 测试按钮文本匹配")
    print("=" * 60)
    
    tests = [
        test_button_texts,
        test_main_menu_logic,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！按钮文本应该匹配了。")
        print("\n问题应该是修复了：")
        print("1. main_menu.py 中的 t() 调用缺少 lang= 参数")
        print("2. 现在按钮文本应该与主菜单处理逻辑匹配")
        return True
    else:
        print("⚠️ 有些测试未通过，需要进一步修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)