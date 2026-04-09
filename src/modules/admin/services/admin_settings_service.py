from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.modules.admin.repositories.agent_commission_repository import (
    AgentCommissionRepository,
)
from src.modules.admin.repositories.bet_limit_repository import BetLimitRepository
from src.modules.admin.repositories.bonus_payout_repository import (
    BonusPayoutRepository,
)
from src.modules.admin.repositories.risk_control_repository import (
    RiskControlRepository,
)
from src.i18n.translator import t


class AdminSettingsService:
    BONUS_DEFAULTS = {
        "MNMT_2C_LO": "70",
        "MNMT_2C_DD": "70",
        "MNMT_2C_DA": "700",
        "MNMT_2C_DX": "500",
        "MNMT_3C_LO": "600",
        "MNMT_3C_XC": "600",
        "MNMT_4C_LO": "6000",
        "MNMT_4C_XC": "6000",
        "MB_2C_LO": "75",
        "MB_2C_DD": "75",
        "MB_2C_DA": "600",
        "MB_3C_LO": "600",
        "MB_3C_XC": "600",
        "MB_4C_LO": "6000",
        "MB_4C_XC": "6000",
    }

    LIMIT_DEFAULTS = {
        "MNMT_2C_LO": "100",
        "MNMT_2C_DD": "100",
        "MNMT_2C_DA": "100",
        "MNMT_2C_DX": "100",
        "MNMT_3C_LO": "200",
        "MNMT_3C_XC": "100",
        "MNMT_4C_LO": "300",
        "MNMT_4C_XC": "100",
        "MB_2C_LO": "100",
        "MB_2C_DD": "100",
        "MB_2C_DA": "100",
        "MB_3C_LO": "200",
        "MB_3C_XC": "100",
        "MB_4C_LO": "300",
        "MB_4C_XC": "100",
    }

    RISK_ACTION_KEY = "OVER_LIMIT_ACTION"
    RISK_ACTION_ACCEPT = "ACCEPT"
    RISK_ACTION_REJECT = "REJECT"
    CUSTOMER_NOTIFICATION_KEY = "CUSTOMER_NOTIFICATION_ENABLED"
    CUSTOMER_NOTIFICATION_ENABLED = "ON"
    CUSTOMER_NOTIFICATION_DISABLED = "OFF"
    SYSTEM_TIME_ZONE_KEY = "SYSTEM_TIME_ZONE"
    DEFAULT_TIMEZONE = "Asia/Kuala_Lumpur"
    ALLOWED_TIMEZONES = {
        "Asia/Kuala_Lumpur": timezone(timedelta(hours=8), name="Asia/Kuala_Lumpur"),
        "Asia/Ho_Chi_Minh": timezone(timedelta(hours=7), name="Asia/Ho_Chi_Minh"),
    }
    CUTOFF_TIME_KEYS = {
        "MN": "MN_CUTOFF_TIME",
        "MT": "MT_CUTOFF_TIME",
        "MB": "MB_CUTOFF_TIME",
    }
    CUTOFF_TIME_DEFAULTS = {
        "MN": "17:10",
        "MT": "18:10",
        "MB": "19:10",
    }

    BONUS_ALLOWED_KEYS = {
        "MN/MT": ["2C_LO", "2C_DD", "2C_DA", "2C_DX", "3C_LO", "3C_XC", "4C_LO", "4C_XC"],
        "MB": ["2C_LO", "2C_DD", "2C_DA", "3C_LO", "3C_XC", "4C_LO", "4C_XC"],
    }

    LIMIT_ALLOWED_KEYS = {
        "MN/MT": ["2C_LO", "2C_DD", "2C_DA", "2C_DX", "3C_LO", "3C_XC", "4C_LO", "4C_XC"],
        "MB": ["2C_LO", "2C_DD", "2C_DA", "3C_LO", "3C_XC", "4C_LO", "4C_XC"],
    }

    def __init__(
        self,
        agent_repo: AgentCommissionRepository | None = None,
        bonus_repo: BonusPayoutRepository | None = None,
        limit_repo: BetLimitRepository | None = None,
        risk_repo: RiskControlRepository | None = None,
    ):
        self.agent_repo = agent_repo or AgentCommissionRepository()
        self.bonus_repo = bonus_repo or BonusPayoutRepository()
        self.limit_repo = limit_repo or BetLimitRepository()
        self.risk_repo = risk_repo or RiskControlRepository()

    def init_and_sync(self) -> None:
        self.agent_repo.init_table()
        self.agent_repo.ensure_default("0")

        self.bonus_repo.init_table()
        self.bonus_repo.ensure_defaults(self.BONUS_DEFAULTS)

        self.limit_repo.init_table()
        self.limit_repo.ensure_defaults(self.LIMIT_DEFAULTS)

        self.risk_repo.init_table()
        self.risk_repo.ensure_default(self.RISK_ACTION_KEY, self.RISK_ACTION_ACCEPT)
        self.risk_repo.ensure_default(self.CUSTOMER_NOTIFICATION_KEY, self.CUSTOMER_NOTIFICATION_ENABLED)
        self.risk_repo.ensure_default(self.SYSTEM_TIME_ZONE_KEY, self.DEFAULT_TIMEZONE)
        for region_group, default_time in self.CUTOFF_TIME_DEFAULTS.items():
            self.risk_repo.ensure_default(self.CUTOFF_TIME_KEYS[region_group], default_time)

    @staticmethod
    def _to_decimal_str(value: str) -> str:
        raw = str(value).strip()
        try:
            dec = Decimal(raw)
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid numeric value: {value}")

        if dec < 0:
            raise ValueError(f"Negative value not allowed: {value}")

        if dec == dec.to_integral():
            return str(int(dec))
        return format(dec.normalize(), "f").rstrip("0").rstrip(".")

    @staticmethod
    def _region_prefix(region_group: str) -> str:
        return "MB" if str(region_group).upper().strip() == "MB" else "MNMT"

    @staticmethod
    def _normalize_time_str(value: str) -> str:
        raw = str(value).strip()
        try:
            parsed = datetime.strptime(raw, "%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format: {value}. Use HH:MM")
        return parsed.strftime("%H:%M")

    def get_agent_commission_rate(self) -> str:
        return self.agent_repo.get_current_rate()

    def set_agent_commission_rate(self, rate: str) -> str:
        normalized = self._to_decimal_str(rate)
        self.agent_repo.set_rate(normalized)
        return normalized

    def get_bonus_payout_map(self) -> dict[str, str]:
        merged = dict(self.BONUS_DEFAULTS)
        merged.update(self.bonus_repo.get_all())
        return merged

    def get_limit_map(self) -> dict[str, str]:
        merged = dict(self.LIMIT_DEFAULTS)
        merged.update(self.limit_repo.get_all())
        return merged

    def get_over_limit_action(self) -> str:
        return (
            self.risk_repo.get(self.RISK_ACTION_KEY, self.RISK_ACTION_ACCEPT)
            or self.RISK_ACTION_ACCEPT
        ).upper()

    def set_over_limit_action(self, action: str) -> str:
        action = str(action).strip().upper()
        if action not in {self.RISK_ACTION_ACCEPT, self.RISK_ACTION_REJECT}:
            raise ValueError("Invalid over limit action")
        self.risk_repo.set(self.RISK_ACTION_KEY, action)
        return action

    def is_customer_notification_enabled(self) -> bool:
        return (
            self.risk_repo.get(
                self.CUSTOMER_NOTIFICATION_KEY,
                self.CUSTOMER_NOTIFICATION_ENABLED,
            )
            or self.CUSTOMER_NOTIFICATION_ENABLED
        ).upper() == self.CUSTOMER_NOTIFICATION_ENABLED

    def get_system_timezone_name(self) -> str:
        value = self.risk_repo.get(self.SYSTEM_TIME_ZONE_KEY, self.DEFAULT_TIMEZONE) or self.DEFAULT_TIMEZONE
        value = str(value).strip()
        if value not in self.ALLOWED_TIMEZONES:
            return self.DEFAULT_TIMEZONE
        return value

    def set_system_timezone_name(self, timezone_name: str) -> str:
        timezone_name = str(timezone_name).strip()
        if timezone_name not in self.ALLOWED_TIMEZONES:
            raise ValueError("Invalid system time zone")
        self.risk_repo.set(self.SYSTEM_TIME_ZONE_KEY, timezone_name)
        return timezone_name

    def get_timezone(self):
        timezone_name = self.get_system_timezone_name()
        try:
            return ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            return self.ALLOWED_TIMEZONES[timezone_name]

    def get_cutoff_time(self, region_group: str) -> str:
        normalized_region = str(region_group).upper().strip()
        setting_key = self.CUTOFF_TIME_KEYS.get(normalized_region)
        if not setting_key:
            raise ValueError(f"Unsupported region group: {region_group}")
        return self._normalize_time_str(
            self.risk_repo.get(setting_key, self.CUTOFF_TIME_DEFAULTS[normalized_region])
            or self.CUTOFF_TIME_DEFAULTS[normalized_region]
        )

    def set_cutoff_time(self, region_group: str, value: str) -> str:
        normalized_region = str(region_group).upper().strip()
        setting_key = self.CUTOFF_TIME_KEYS.get(normalized_region)
        if not setting_key:
            raise ValueError(f"Unsupported region group: {region_group}")
        normalized_time = self._normalize_time_str(value)
        self.risk_repo.set(setting_key, normalized_time)
        return normalized_time

    def format_cutoff_time_text(self, lang: str = "en") -> str:
        return "\n".join(
            [
                t("ADMIN_FORMAT_BET_TIME_LIMIT", lang),
                "",
                f"MN: {self.get_cutoff_time('MN')}",
                f"MT: {self.get_cutoff_time('MT')}",
                f"MB: {self.get_cutoff_time('MB')}",
                "",
                t("ADMIN_FORMAT_TIMEZONE_LINE", lang, tz=self.get_system_timezone_name()),
            ]
        )

    def format_system_timezone_text(self, lang: str = "en") -> str:
        return "\n".join(
            [
                t("ADMIN_FORMAT_SYSTEM_TIME_ZONE", lang),
                "",
                t("ADMIN_FORMAT_CURRENT_LINE", lang, value=self.get_system_timezone_name()),
            ]
        )

    def build_cutoff_time_edit_template(self) -> str:
        return "\n".join(
            [
                f"MN={self.get_cutoff_time('MN')}",
                f"MT={self.get_cutoff_time('MT')}",
                f"MB={self.get_cutoff_time('MB')}",
            ]
        )

    def update_cutoff_time_bulk(self, text: str) -> None:
        values: dict[str, str] = {}
        for raw_line in str(text).splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if "=" not in line:
                raise ValueError(f"Invalid line: {line}")
            key, value = line.split("=", 1)
            region_group = key.strip().upper()
            if region_group not in self.CUTOFF_TIME_KEYS:
                raise ValueError(f"Invalid region: {region_group}")
            values[region_group] = self._normalize_time_str(value)

        missing = [r for r in self.CUTOFF_TIME_KEYS if r not in values]
        if missing:
            raise ValueError(f"Missing cutoff time for: {', '.join(missing)}")

        for region_group, time_value in values.items():
            self.set_cutoff_time(region_group, time_value)

    def set_customer_notification_enabled(self, enabled: bool) -> str:
        value = (
            self.CUSTOMER_NOTIFICATION_ENABLED
            if enabled
            else self.CUSTOMER_NOTIFICATION_DISABLED
        )
        self.risk_repo.set(self.CUSTOMER_NOTIFICATION_KEY, value)
        return value

    def toggle_customer_notification_enabled(self) -> str:
        return self.set_customer_notification_enabled(
            not self.is_customer_notification_enabled()
        )

    def get_bonus_payout_value(self, region_group: str, local_key: str) -> str:
        full_key = f"{self._region_prefix(region_group)}_{local_key}"
        return self.get_bonus_payout_map().get(
            full_key,
            self.BONUS_DEFAULTS.get(full_key, "0"),
        )

    def get_limit_value(self, region_group: str, local_key: str) -> str:
        full_key = f"{self._region_prefix(region_group)}_{local_key}"
        return self.get_limit_map().get(
            full_key,
            self.LIMIT_DEFAULTS.get(full_key, "0"),
        )

    def format_bonus_payout_text(self, lang: str = "en") -> str:
        return self._format_structured_text(
            title=t("ADMIN_FORMAT_BONUS_PAYOUT_SETTINGS", lang),
            values=self.get_bonus_payout_map(),
            include_action=None,
        )

    def format_limit_text(self, lang: str = "en") -> str:
        return self._format_structured_text(
            title=t("ADMIN_FORMAT_OVER_LIMIT_SETTINGS", lang),
            values=self.get_limit_map(),
            include_action=self.get_over_limit_action(),
        )

    def format_notification_text(self, lang: str = "en") -> str:
        status = (
            self.CUSTOMER_NOTIFICATION_ENABLED
            if self.is_customer_notification_enabled()
            else self.CUSTOMER_NOTIFICATION_DISABLED
        )
        return "\n".join(
            [
                t("ADMIN_FORMAT_NOTIFICATIONS", lang),
                "",
                t("ADMIN_FORMAT_CUSTOMER_NOTIF", lang, status=status),
                t("ADMIN_FORMAT_OVER_LIMIT_ACTION", lang, action=self.get_over_limit_action()),
            ]
        )

    def build_bonus_edit_template(self) -> str:
        return self._build_bulk_template(self.get_bonus_payout_map())

    def build_limit_edit_template(self) -> str:
        return self._build_bulk_template(self.get_limit_map())

    def update_bonus_payout_bulk(self, text: str) -> None:
        parsed = self._parse_bulk_text(text, self.BONUS_ALLOWED_KEYS)
        self.bonus_repo.upsert_many(parsed)

    def update_limit_bulk(self, text: str) -> None:
        parsed = self._parse_bulk_text(text, self.LIMIT_ALLOWED_KEYS)
        self.limit_repo.upsert_many(parsed)

    def _build_bulk_template(self, values: dict[str, str]) -> str:
        lines = [
            "MN/MT",
            f"2C_LO={values.get('MNMT_2C_LO', '')}",
            f"2C_DD={values.get('MNMT_2C_DD', '')}",
            f"2C_DA={values.get('MNMT_2C_DA', '')}",
            f"2C_DX={values.get('MNMT_2C_DX', '')}",
            "",
            f"3C_LO={values.get('MNMT_3C_LO', '')}",
            f"3C_XC={values.get('MNMT_3C_XC', '')}",
            "",
            f"4C_LO={values.get('MNMT_4C_LO', '')}",
            f"4C_XC={values.get('MNMT_4C_XC', '')}",
            "",
            "MB",
            f"2C_LO={values.get('MB_2C_LO', '')}",
            f"2C_DD={values.get('MB_2C_DD', '')}",
            f"2C_DA={values.get('MB_2C_DA', '')}",
            "",
            f"3C_LO={values.get('MB_3C_LO', '')}",
            f"3C_XC={values.get('MB_3C_XC', '')}",
            "",
            f"4C_LO={values.get('MB_4C_LO', '')}",
            f"4C_XC={values.get('MB_4C_XC', '')}",
        ]
        return "\n".join(lines)

    def _format_structured_text(
        self,
        title: str,
        values: dict[str, str],
        include_action: str | None,
    ) -> str:
        lines = [
            title,
            "",
            "MN/MT",
            "2C",
            f"  LO: {values.get('MNMT_2C_LO', '')}",
            f"  DD: {values.get('MNMT_2C_DD', '')}",
            f"  DA: {values.get('MNMT_2C_DA', '')}",
            f"  DX: {values.get('MNMT_2C_DX', '')}",
            "",
            "3C",
            f"  LO: {values.get('MNMT_3C_LO', '')}",
            f"  XC: {values.get('MNMT_3C_XC', '')}",
            "",
            "4C",
            f"  LO: {values.get('MNMT_4C_LO', '')}",
            f"  XC: {values.get('MNMT_4C_XC', '')}",
            "",
            "MB",
            "2C",
            f"  LO: {values.get('MB_2C_LO', '')}",
            f"  DD: {values.get('MB_2C_DD', '')}",
            f"  DA: {values.get('MB_2C_DA', '')}",
            "",
            "3C",
            f"  LO: {values.get('MB_3C_LO', '')}",
            f"  XC: {values.get('MB_3C_XC', '')}",
            "",
            "4C",
            f"  LO: {values.get('MB_4C_LO', '')}",
            f"  XC: {values.get('MB_4C_XC', '')}",
        ]

        if include_action is not None:
            lines.extend(["", f"Action: {include_action}"])

        return "\n".join(lines)

    def _parse_bulk_text(
        self,
        text: str,
        allowed_structure: dict[str, list[str]],
    ) -> dict[str, str]:
        lines = [line.strip() for line in str(text).splitlines()]
        current_section = None
        section_values: dict[str, dict[str, str]] = {"MN/MT": {}, "MB": {}}

        for raw in lines:
            if not raw:
                continue
            if raw.upper() == "MN/MT":
                current_section = "MN/MT"
                continue
            if raw.upper() == "MB":
                current_section = "MB"
                continue
            if current_section is None:
                raise ValueError("Missing section header. Use MN/MT and MB.")
            if "=" not in raw:
                raise ValueError(f"Invalid line: {raw}")

            key, value = raw.split("=", 1)
            key = key.strip().upper()
            value = value.strip()
            if key not in allowed_structure[current_section]:
                raise ValueError(f"Invalid key in {current_section}: {key}")
            section_values[current_section][key] = self._to_decimal_str(value)

        for section_name, keys in allowed_structure.items():
            missing = [k for k in keys if k not in section_values[section_name]]
            if missing:
                raise ValueError(
                    f"Missing keys in {section_name}: {', '.join(missing)}"
                )

        result: dict[str, str] = {}
        for key, value in section_values["MN/MT"].items():
            result[f"MNMT_{key}"] = value
        for key, value in section_values["MB"].items():
            result[f"MB_{key}"] = value
        return result
