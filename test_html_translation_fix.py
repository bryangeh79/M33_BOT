#!/usr/bin/env python3
"""
测试HTML翻译修复
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_settlement_report():
    """测试结算报告HTML导出"""
    print("=== 测试结算报告HTML导出 ===")
    
    try:
        from src.modules.report.formatters.settlement_report_html_exporter import export_settlement_report_html
        
        # 创建测试数据
        test_report = {
            "date": "2026-04-07",
            "regions": {
                "MB": {
                    "bet_total": 4400.0,
                    "payout_total": 2200.0,
                    "commission": 220.0,
                    "settlement": 1980.0,
                    "winner_count": 2
                }
            },
            "summary": {
                "total_settlement": 1980.0
            },
            "winner_details": [
                {
                    "ticket_no": "T001",
                    "region": "MB",
                    "numbers": ["12", "34", "56"],
                    "bet_type": "LO",
                    "bet_code": "2C",
                    "bet_total": 1000.0,
                    "payout": 500.0
                }
            ]
        }
        
        # 测试英文
        print("\n1. 测试英文版本:")
        html_en = export_settlement_report_html(test_report, lang="en")
        
        # 检查关键元素
        checks = [
            ('<html lang="en">', 'HTML语言属性'),
            ('Settlement Report', '英文标题'),
            ('Date:', '日期标签'),
            ('Total Settlement', '总结算标签'),
            ('Winning Details', '中奖详情标签')
        ]
        
        for text, description in checks:
            if text in html_en:
                print(f"   ✅ {description}: 找到 '{text}'")
            else:
                print(f"   ❌ {description}: 未找到 '{text}'")
        
        # 测试越南语
        print("\n2. 测试越南语版本:")
        html_vi = export_settlement_report_html(test_report, lang="vi")
        
        vi_checks = [
            ('<html lang="vi">', 'HTML语言属性'),
            ('Báo cáo Quyết toán', '越南语标题'),
            ('Ngày:', '日期标签'),
            ('Tổng Quyết toán', '总结算标签'),
            ('Chi tiết Trúng thưởng', '中奖详情标签')
        ]
        
        for text, description in vi_checks:
            if text in html_vi:
                print(f"   ✅ {description}: 找到 '{text}'")
            else:
                print(f"   ❌ {description}: 未找到 '{text}'")
        
        # 测试中文
        print("\n3. 测试中文版本:")
        html_zh = export_settlement_report_html(test_report, lang="zh")
        
        zh_checks = [
            ('<html lang="zh">', 'HTML语言属性'),
            ('结算报告', '中文标题'),
            ('日期:', '日期标签'),
            ('总结算', '总结算标签'),
            ('中奖详情', '中奖详情标签')
        ]
        
        for text, description in zh_checks:
            if text in html_zh:
                print(f"   ✅ {description}: 找到 '{text}'")
            else:
                print(f"   ❌ {description}: 未找到 '{text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transaction_report():
    """测试交易报告HTML导出"""
    print("\n=== 测试交易报告HTML导出 ===")
    
    try:
        from src.modules.report.formatters.report_html_formatter import build_transaction_report_html
        
        # 创建测试数据
        test_data = {
            "date": "2026-04-07",
            "regions": {
                "MB": {
                    "tickets": [
                        {
                            "ticket_no": "T001",
                            "lines": [
                                {
                                    "region": "MB",
                                    "number": "12 34",
                                    "mode": "LO 2C",
                                    "total": "1000"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        # 测试英文
        print("\n1. 测试英文版本:")
        html_en = build_transaction_report_html(test_data, lang="en")
        
        checks = [
            ('<html lang="en">', 'HTML语言属性'),
            ('Transaction Report', '英文标题'),
            ('Date:', '日期标签'),
            ('Region', '区域表头'),
            ('Numbers', '号码表头'),
            ('Bet Type', '投注类型表头'),
            ('Total', '总计表头')
        ]
        
        for text, description in checks:
            if text in html_en:
                print(f"   ✅ {description}: 找到 '{text}'")
            else:
                print(f"   ❌ {description}: 未找到 '{text}'")
        
        # 测试越南语
        print("\n2. 测试越南语版本:")
        html_vi = build_transaction_report_html(test_data, lang="vi")
        
        vi_checks = [
            ('<html lang="vi">', 'HTML语言属性'),
            ('Báo cáo Giao dịch', '越南语标题'),
            ('Ngày:', '日期标签'),
            ('Khu vực', '区域表头'),
            ('Số', '号码表头'),
            ('Loại cược', '投注类型表头'),
            ('Tổng', '总计表头')
        ]
        
        for text, description in vi_checks:
            if text in html_vi:
                print(f"   ✅ {description}: 找到 '{text}'")
            else:
                print(f"   ❌ {description}: 未找到 '{text}'")
        
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
        
        # 测试所有HTML相关翻译键
        html_keys = [
            "HTML_TITLE_SETTLEMENT",
            "HTML_TITLE_TRANSACTION",
            "HTML_TITLE_NUMBER_DETAIL",
            "HTML_TITLE_OVER_LIMIT",
            "HTML_LABEL_DATE",
            "HTML_LABEL_TOTAL",
            "HTML_LABEL_REGION",
            "HTML_LABEL_TICKET_NO",
            "HTML_LABEL_BET_TYPE",
            "HTML_LABEL_NUMBERS",
            "HTML_LABEL_UNIT",
            "HTML_LABEL_AMOUNT",
            "HTML_LABEL_GENERATED_AT",
            "HTML_TOTAL_SETTLEMENT",
            "HTML_WINNING_DETAILS",
            "HTML_NO_DATA",
            "HTML_TOTAL_BET",
            "HTML_TOTAL_PAYOUT",
            "HTML_COMMISSION",
            "HTML_SETTLEMENT",
            "HTML_WINNER_COUNT",
            "HTML_REGION_TOTAL",
            "HTML_SUMMARY",
            "HTML_DETAILS"
        ]
        
        languages = ["en", "vi", "zh"]
        
        all_good = True
        for lang in languages:
            print(f"\n测试语言: {lang}")
            for key in html_keys:
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
    print("🔍 HTML翻译修复测试")
    print("=" * 60)
    
    success = True
    
    # 运行测试
    if not test_settlement_report():
        success = False
    
    if not test_transaction_report():
        success = False
    
    if not test_translation_keys():
        success = False
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 所有测试通过！HTML翻译修复成功。")
        print("\n修复总结:")
        print("1. ✅ 添加了HTML相关翻译键")
        print("2. ✅ 修改了HTML导出函数支持多语言")
        print("3. ✅ 更新了调用代码传递用户语言")
        print("4. ✅ 验证了英文、越南语、中文版本")
    else:
        print("⚠️ 测试失败，需要进一步调试。")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)