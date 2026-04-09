from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from src.modules.admin.services.admin_settings_service import AdminSettingsService
from src.modules.report.helpers.report_normalizer import ReportNormalizer
from src.modules.report.repositories.report_repository import ReportRepository


class OverLimitReportService:
    def __init__(
        self,
        repo: ReportRepository | None = None,
        admin_settings_service: AdminSettingsService | None = None,
    ):
        self.repo = repo or ReportRepository()
        self.admin_settings_service = admin_settings_service or AdminSettingsService()

    def generate(self, target_date: str) -> dict[str, Any]:
        rows = self.repo.get_number_detail_rows(target_date)

        normal_groups = defaultdict(lambda: Decimal('0'))
        da_groups = defaultdict(lambda: Decimal('0'))
        dx_groups = defaultdict(lambda: Decimal('0'))

        for row in rows:
            parsed = self._parse_row(row)
            category = parsed['category']

            if category == 'NORMAL':
                key = (
                    parsed['region_group'],
                    parsed['section'],
                    parsed['region_code'],
                    parsed['play_type'],
                    parsed['number'],
                    parsed['limit_local_key'],
                )
                normal_groups[key] += parsed['amount']

            elif category == 'DA':
                key = (
                    parsed['region_group'],
                    parsed['region_code'],
                    parsed['number_group'],
                    parsed['limit_local_key'],
                )
                da_groups[key] += parsed['amount']

            elif category == 'DX':
                key = (
                    parsed['region_group'],
                    parsed['region_combo'],
                    parsed['number_group'],
                    parsed['limit_local_key'],
                )
                dx_groups[key] += parsed['amount']

        result = {
            'date': target_date,
            'groups': {
                'MN': self._empty_group(),
                'MT': self._empty_group(),
                'MB': self._empty_group(),
            },
            'summary': {
                'normal_over_count': 0,
                'da_over_count': 0,
                'dx_over_count': 0,
                'total_over_count': 0,
            },
        }

        self._build_normal_section(result, normal_groups)
        self._build_da_section(result, da_groups)
        self._build_dx_section(result, dx_groups)
        result['summary']['total_over_count'] = (
            result['summary']['normal_over_count']
            + result['summary']['da_over_count']
            + result['summary']['dx_over_count']
        )
        return result

    @staticmethod
    def _empty_group() -> dict[str, Any]:
        return {
            '2c': defaultdict(list),
            '3c': defaultdict(list),
            '4c': defaultdict(list),
            'da': defaultdict(list),
            'dx': [],
        }

    def _build_normal_section(self, result: dict[str, Any], normal_groups: dict[tuple, Decimal]) -> None:
        for key, total_amount in normal_groups.items():
            region_group, section, region_code, play_type, number, limit_local_key = key
            if limit_local_key == 'UNKNOWN':
                continue
            limit_value = Decimal(self.admin_settings_service.get_limit_value(region_group, limit_local_key))
            over_amount = total_amount - limit_value
            if over_amount <= 0:
                continue
            result['groups'][region_group][section][region_code].append(
                {
                    'number': number,
                    'play_type': play_type.lower(),
                    'over_amount': over_amount,
                    'total_amount': total_amount,
                    'limit_amount': limit_value,
                }
            )
            result['summary']['normal_over_count'] += 1

        for region_group in ('MN', 'MT', 'MB'):
            for section in ('2c', '3c', '4c'):
                section_dict = result['groups'][region_group][section]
                for region_code, items in section_dict.items():
                    items.sort(key=lambda x: (str(x['number']), str(x['play_type']), x['over_amount']))

    def _build_da_section(self, result: dict[str, Any], da_groups: dict[tuple, Decimal]) -> None:
        for key, total_amount in da_groups.items():
            region_group, region_code, number_group, limit_local_key = key
            limit_value = Decimal(self.admin_settings_service.get_limit_value(region_group, limit_local_key))
            over_amount = total_amount - limit_value
            if over_amount <= 0:
                continue
            result['groups'][region_group]['da'][region_code].append(
                {
                    'number_group': number_group,
                    'over_amount': over_amount,
                    'total_amount': total_amount,
                    'limit_amount': limit_value,
                }
            )
            result['summary']['da_over_count'] += 1

        for region_group in ('MN', 'MT', 'MB'):
            da_dict = result['groups'][region_group]['da']
            for region_code, items in da_dict.items():
                items.sort(key=lambda x: str(x['number_group']))

    def _build_dx_section(self, result: dict[str, Any], dx_groups: dict[tuple, Decimal]) -> None:
        for key, total_amount in dx_groups.items():
            region_group, region_combo, number_group, limit_local_key = key
            if region_group == 'MB':
                continue
            limit_value = Decimal(self.admin_settings_service.get_limit_value(region_group, limit_local_key))
            over_amount = total_amount - limit_value
            if over_amount <= 0:
                continue
            result['groups'][region_group]['dx'].append(
                {
                    'region_combo': region_combo,
                    'number_group': number_group,
                    'over_amount': over_amount,
                    'total_amount': total_amount,
                    'limit_amount': limit_value,
                }
            )
            result['summary']['dx_over_count'] += 1

        for region_group in ('MN', 'MT'):
            result['groups'][region_group]['dx'].sort(key=lambda x: (str(x['region_combo']), str(x['number_group'])))

    def _parse_row(self, row: dict[str, Any]) -> dict[str, Any]:
        region_group = str(row.get('region_group', '')).upper()
        region_code = str(row.get('region_code', '')).strip().lower()
        bet_type = str(row.get('bet_type', '')).strip().upper()
        amount = ReportNormalizer.to_decimal(row.get('amount'))
        input_text = str(row.get('input_text', '')).strip().lower()

        tokens = [t for t in input_text.split() if t.strip()]
        number_tokens = [t for t in tokens if t.isdigit()]

        if bet_type == 'DA':
            return {
                'category': 'DA',
                'region_group': region_group,
                'region_code': region_code,
                'number_group': ' '.join(number_tokens),
                'amount': amount,
                'limit_local_key': '2C_DA',
            }

        if bet_type == 'DX':
            region_combo = ' '.join([p.strip().lower() for p in str(row.get('region_code', '')).split(',') if p.strip()])
            return {
                'category': 'DX',
                'region_group': region_group,
                'region_combo': region_combo,
                'number_group': ' '.join(number_tokens),
                'amount': amount,
                'limit_local_key': '2C_DX',
            }

        return self._parse_normal_bet(
            region_group=region_group,
            region_code=region_code,
            bet_type=bet_type,
            number_tokens=number_tokens,
            amount=amount,
        )

    @staticmethod
    def _parse_normal_bet(
        *,
        region_group: str,
        region_code: str,
        bet_type: str,
        number_tokens: list[str],
        amount: Decimal,
    ) -> dict[str, Any]:
        number = number_tokens[0] if number_tokens else ''
        digit_len = len(number)

        if bet_type == 'LO':
            if digit_len == 2:
                section = '2c'
                limit_local_key = '2C_LO'
            elif digit_len == 3:
                section = '3c'
                limit_local_key = '3C_LO'
            elif digit_len == 4:
                section = '4c'
                limit_local_key = '4C_LO'
            else:
                section = 'unknown'
                limit_local_key = 'UNKNOWN'
        elif bet_type == 'DD':
            section = '2c'
            limit_local_key = '2C_DD'
        elif bet_type == 'XC':
            if digit_len == 3:
                section = '3c'
                limit_local_key = '3C_XC'
            elif digit_len == 4:
                section = '4c'
                limit_local_key = '4C_XC'
            else:
                section = 'unknown'
                limit_local_key = 'UNKNOWN'
        else:
            section = 'unknown'
            limit_local_key = 'UNKNOWN'

        return {
            'category': 'NORMAL',
            'region_group': region_group,
            'section': section,
            'region_code': region_code,
            'play_type': bet_type,
            'number': number,
            'amount': amount,
            'limit_local_key': limit_local_key,
        }
