import re
from decimal import Decimal, InvalidOperation
from typing import Any


class ReportNormalizer:
    AMOUNT_SUFFIX_PATTERN = re.compile(r"(\d+(?:\.\d+)?)n\b", re.IGNORECASE)
    PURE_NUMBER_PATTERN = re.compile(r"^\d+$")

    @staticmethod
    def to_decimal(value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value

        if value is None:
            return Decimal("0")

        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def format_decimal(value: Decimal | str | int | float) -> str:
        dec = ReportNormalizer.to_decimal(value)
        if dec == dec.to_integral():
            return str(int(dec))
        return format(dec.normalize(), "f").rstrip("0").rstrip(".")

    @staticmethod
    def _clean_region_key(region_code: str | None) -> str:
        if not region_code:
            return ""
        parts = [p.strip().lower() for p in str(region_code).replace(" ", "").split(",") if p.strip()]
        return ",".join(parts)

    @staticmethod
    def _extract_number_key(input_text: str | None) -> str:
        if not input_text:
            return ""

        tokens = str(input_text).strip().lower().split()
        number_tokens = [t for t in tokens if ReportNormalizer.PURE_NUMBER_PATTERN.match(t)]
        return ",".join(number_tokens)

    @staticmethod
    def normalize_transaction_item(item: dict[str, Any]) -> str:
        """
        生成 Transaction Report 标准展示行：
        - 不带 n
        - 一行一注
        - 保留组合结构
        """
        raw = str(item.get("input_text", "")).strip().lower()
        raw = re.sub(r"\s+", " ", raw)
        raw = ReportNormalizer.AMOUNT_SUFFIX_PATTERN.sub(r"\1", raw)
        return raw

    @staticmethod
    def normalize_number_detail_item(item: dict[str, Any]) -> dict[str, Any]:
        """
        Report 层统一原子结构：
        区域 | 号码 | 玩法 | 数目
        """
        region_group = str(item.get("region_group", "")).upper()
        region_key = ReportNormalizer._clean_region_key(item.get("region_code"))
        number_key = ReportNormalizer._extract_number_key(item.get("input_text"))
        bet_type = str(item.get("bet_type", "")).upper()
        amount = ReportNormalizer.to_decimal(item.get("amount"))

        return {
            "region_group": region_group,
            "region_key": region_key,
            "number_key": number_key,
            "bet_type": bet_type,
            "amount": amount,
        }