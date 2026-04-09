#!/usr/bin/env python3
"""
调试HTML输出
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_transaction_report():
    """调试交易报告HTML输出"""
    print("=== 调试交易报告HTML输出 ===")
    
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
        
        # 生成英文HTML
        html_en = build_transaction_report_html(test_data, lang="en")
        
        # 查找表头部分
        print("\n英文HTML表头部分:")
        lines = html_en.split('\n')
        for i, line in enumerate(lines):
            if 'Region' in line or 'Number' in line or 'Mode' in line or 'Total' in line:
                print(f"第{i+1}行: {line.strip()}")
        
        # 特别查找<th>标签
        print("\n查找<th>标签:")
        for i, line in enumerate(lines):
            if '<th' in line:
                print(f"第{i+1}行: {line.strip()}")
        
        # 保存HTML文件以便查看
        with open('debug_transaction_en.html', 'w', encoding='utf-8') as f:
            f.write(html_en)
        print("\n✅ 已保存英文HTML到: debug_transaction_en.html")
        
        # 生成越南语HTML
        html_vi = build_transaction_report_html(test_data, lang="vi")
        
        print("\n越南语HTML表头部分:")
        lines_vi = html_vi.split('\n')
        for i, line in enumerate(lines_vi):
            if 'Khu vực' in line or 'Số' in line or 'Loại cược' in line or 'Tổng' in line:
                print(f"第{i+1}行: {line.strip()}")
        
        with open('debug_transaction_vi.html', 'w', encoding='utf-8') as f:
            f.write(html_vi)
        print("✅ 已保存越南语HTML到: debug_transaction_vi.html")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_transaction_report()