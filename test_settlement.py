from pprint import pprint

from src.modules.settlement.services.settlement_service import settle_region

# 用你数据库里确认存在的组合
DRAW_DATE = "2026-03-17"
REGION_GROUP = "MN"

result = settle_region(DRAW_DATE, REGION_GROUP)
pprint(result)