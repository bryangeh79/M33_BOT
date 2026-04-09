from pathlib import Path
from pprint import pprint

from src.modules.report.services.settlement_report_service import SettlementReportService
from src.modules.report.formatters.settlement_report_formatter import (
    format_settlement_report_telegram,
)
from src.modules.report.formatters.settlement_report_html_exporter import (
    export_settlement_report_html,
)

TARGET_DATE = "2026-03-17"
AGENT_COMMISSION_RATE = 0

service = SettlementReportService()
report = service.generate_report(
    target_date=TARGET_DATE,
    agent_commission_rate=AGENT_COMMISSION_RATE,
)

print("===== TELEGRAM TEXT =====")
telegram_text = format_settlement_report_telegram(report)
print(telegram_text)

print("\n===== RAW REPORT DICT =====")
pprint(report)

html = export_settlement_report_html(report)
output_path = Path("settlement_report_2026_03_17.html")
output_path.write_text(html, encoding="utf-8")

print(f"\nHTML exported to: {output_path.resolve()}")