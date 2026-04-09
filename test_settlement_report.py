from pprint import pprint

from src.modules.report.services.settlement_report_service import SettlementReportService

TARGET_DATE = "2026-03-17"

# 先用 0 测
AGENT_COMMISSION_RATE = 0

service = SettlementReportService()
result = service.generate_report(
    target_date=TARGET_DATE,
    agent_commission_rate=AGENT_COMMISSION_RATE,
)

pprint(result)