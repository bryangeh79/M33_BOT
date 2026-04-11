from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


class XosodaiphatResultParser:
    REGION_PREFIX = {
        "MN": "XSMN",
        "MT": "XSMT",
        "MB": "XSMB",
    }

    STOP_KEYWORDS = (
        "LOTO",
        "THỐNG KÊ",
        "THONG KE",
        "TIN TÀI TRỢ",
        "TIN TAI TRO",
        "QUẢNG CÁO",
        "QUANG CAO",
        "XEM THỐNG KÊ",
        "XEM THONG KE",
        "XEM NHANH",
        "XEM THÊM",
        "XEM THEM",
        "KQXS THEO TỈNH",
        "KQXS THEO TINH",
        "THÔNG TIN VỀ KẾT QUẢ",
        "THONG TIN VE KET QUA",
        "XỔ SỐ TRỰC TIẾP HÔM NAY",
        "XO SO TRUC TIEP HOM NAY",
        "XỔ SỐ HÔM QUA",
        "XO SO HOM QUA",
    )

    MN_MT_PRIZE_SPEC = {
        "G8": {"count": 1, "digits": 2},
        "G7": {"count": 1, "digits": 3},
        "G6": {"count": 3, "digits": 4},
        "G5": {"count": 1, "digits": 4},
        "G4": {"count": 7, "digits": 5},
        "G3": {"count": 2, "digits": 5},
        "G2": {"count": 1, "digits": 5},
        "G1": {"count": 1, "digits": 5},
        "DB": {"count": 1, "digits": 6},
    }

    MB_PRIZE_SPEC = {
        "DB": {"count": 1, "digits": 5},
        "G1": {"count": 1, "digits": 5},
        "G2": {"count": 2, "digits": 5},
        "G3": {"count": 6, "digits": 5},
        "G4": {"count": 4, "digits": 4},
        "G5": {"count": 6, "digits": 4},
        "G6": {"count": 3, "digits": 3},
        "G7": {"count": 4, "digits": 2},
    }

    ALLOWED_PRIZES_MN_MT = ("G8", "G7", "G6", "G5", "G4", "G3", "G2", "G1", "DB")
    ALLOWED_PRIZES_MB = ("DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7")

    DATE_FORMATTERS = (
        lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}",
        lambda y, m, d: f"{d:02d}/{m:02d}/{y:04d}",
        lambda y, m, d: f"{d:02d}-{m:02d}-{y:04d}",
    )

    REGION_PROVINCES = {
        "MN": [
            "TP.HCM", "TPHCM", "HỒ CHÍ MINH", "HO CHI MINH",
            "AN GIANG", "BẠC LIÊU", "BAC LIEU", "BẾN TRE", "BEN TRE",
            "BÌNH DƯƠNG", "BINH DUONG", "BÌNH PHƯỚC", "BINH PHUOC",
            "BÌNH THUẬN", "BINH THUAN", "CÀ MAU", "CA MAU",
            "CẦN THƠ", "CAN THO", "ĐÀ LẠT", "DA LAT", "ĐỒNG NAI", "DONG NAI",
            "ĐỒNG THÁP", "DONG THAP", "HẬU GIANG", "HAU GIANG",
            "KIÊN GIANG", "KIEN GIANG", "LONG AN", "SÓC TRĂNG", "SOC TRANG",
            "TÂY NINH", "TAY NINH", "TIỀN GIANG", "TIEN GIANG",
            "TRÀ VINH", "TRA VINH", "VĨNH LONG", "VINH LONG",
            "VŨNG TÀU", "VUNG TAU",
        ],
        "MT": [
            "BÌNH ĐỊNH", "BINH DINH", "ĐÀ NẴNG", "DA NANG",
            "ĐẮK LẮK", "DAK LAK", "ĐẮK NÔNG", "DAK NONG", "GIA LAI",
            "HUẾ", "HUE", "KHÁNH HÒA", "KHANH HOA", "KON TUM",
            "NINH THUẬN", "NINH THUAN", "PHÚ YÊN", "PHU YEN",
            "QUẢNG BÌNH", "QUANG BINH", "QUẢNG NAM", "QUANG NAM",
            "QUẢNG NGÃI", "QUANG NGAI", "QUẢNG TRỊ", "QUANG TRI",
            "TT.HUẾ", "TT HUE", "THỪA THIÊN HUẾ", "THUA THIEN HUE",
        ],
    }

    PROVINCE_CANONICAL = {
        "TPHCM": ("TPHCM", "TPHCM"),
        "HOCHIMINH": ("TPHCM", "TPHCM"),
        "ANGIANG": ("ANGIANG", "AN GIANG"),
        "BACLIEU": ("BACLIEU", "BẠC LIÊU"),
        "BENTRE": ("BENTRE", "BẾN TRE"),
        "BINHDUONG": ("BINHDUONG", "BÌNH DƯƠNG"),
        "BINHPHUOC": ("BINHPHUOC", "BÌNH PHƯỚC"),
        "BINHTHUAN": ("BINHTHUAN", "BÌNH THUẬN"),
        "CAMAU": ("CAMAU", "CÀ MAU"),
        "CANTHO": ("CANTHO", "CẦN THƠ"),
        "DALAT": ("DALAT", "ĐÀ LẠT"),
        "DONGNAI": ("DONGNAI", "ĐỒNG NAI"),
        "DONGTHAP": ("DONGTHAP", "ĐỒNG THÁP"),
        "HAUGIANG": ("HAUGIANG", "HẬU GIANG"),
        "KIENGIANG": ("KIENGIANG", "KIÊN GIANG"),
        "LONGAN": ("LONGAN", "LONG AN"),
        "SOCTRANG": ("SOCTRANG", "SÓC TRĂNG"),
        "TAYNINH": ("TAYNINH", "TÂY NINH"),
        "TIENGIANG": ("TIENGIANG", "TIỀN GIANG"),
        "TRAVINH": ("TRAVINH", "TRÀ VINH"),
        "VINHLONG": ("VINHLONG", "VĨNH LONG"),
        "VUNGTAU": ("VUNGTAU", "VŨNG TÀU"),
        "BINHDINH": ("BINHDINH", "BÌNH ĐỊNH"),
        "DANANG": ("DANANG", "ĐÀ NẴNG"),
        "DAKLAK": ("DAKLAK", "ĐẮK LẮK"),
        "DAKNONG": ("DAKNONG", "ĐẮK NÔNG"),
        "GIALAI": ("GIALAI", "GIA LAI"),
        "HUE": ("HUE", "HUẾ"),
        "KHANHHOA": ("KHANHHOA", "KHÁNH HÒA"),
        "KONTUM": ("KONTUM", "KON TUM"),
        "NINHTHUAN": ("NINHTHUAN", "NINH THUẬN"),
        "PHUYEN": ("PHUYEN", "PHÚ YÊN"),
        "QUANGBINH": ("QUANGBINH", "QUẢNG BÌNH"),
        "QUANGNAM": ("QUANGNAM", "QUẢNG NAM"),
        "QUANGNGAI": ("QUANGNGAI", "QUẢNG NGÃI"),
        "QUANGTRI": ("QUANGTRI", "QUẢNG TRỊ"),
        "THUATHIENHUE": ("HUE", "HUẾ"),
    }

    @classmethod
    def parse(cls, region_code: str, draw_date: str, html: str) -> List[Dict]:
        region_code = region_code.upper().strip()
        if region_code not in cls.REGION_PREFIX:
            raise ValueError(f"Unsupported region code: {region_code}")

        soup = BeautifulSoup(html, "html.parser")

        if region_code == "MB":
            table_items = cls._parse_mb_from_tables(soup)
            if table_items:
                return table_items

        lines = cls._extract_lines(soup)
        if not lines:
            return []

        start_index = cls._find_block_start(lines, region_code, draw_date)
        if start_index is None:
            return []

        block_lines = cls._collect_block_lines(lines, start_index)
        if not block_lines:
            return []

        if region_code == "MB":
            return cls._parse_mb_block(block_lines)

        return cls._parse_mn_mt_block(region_code, block_lines)

    @classmethod
    def _parse_from_tables(cls, region_code: str, draw_date: str, soup: BeautifulSoup) -> List[Dict]:
        if region_code == "MB":
            return cls._parse_mb_from_tables(soup)
        return cls._parse_mn_mt_from_tables(region_code, soup)

    @classmethod
    def _parse_mn_mt_from_tables(cls, region_code: str, soup: BeautifulSoup) -> List[Dict]:
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 3:
                continue

            header_cells = rows[0].find_all(["th", "td"])
            if len(header_cells) < 4:
                continue

            header_texts = [cls._normalize_line(cell.get_text(" ", strip=True)) for cell in header_cells]
            first_header = cls._ascii_upper(header_texts[0])
            if "GIAI" not in first_header:
                continue

            provinces: List[Tuple[str, str]] = []
            for cell_text in header_texts[1:]:
                province = cls._resolve_province(cell_text)
                if province:
                    provinces.append(province)

            if region_code == "MN" and not (3 <= len(provinces) <= 4):
                continue
            if region_code == "MT" and not (2 <= len(provinces) <= 3):
                continue

            items: List[Dict] = []
            prize_order = 0

            for row in rows[1:]:
                cells = row.find_all(["th", "td"])
                if len(cells) < len(provinces) + 1:
                    continue

                prize_code = cls._normalize_prize_label(cls._normalize_line(cells[0].get_text(" ", strip=True)))
                if prize_code not in cls.ALLOWED_PRIZES_MN_MT:
                    continue

                spec = cls.MN_MT_PRIZE_SPEC[prize_code]
                prize_order += 1

                for province_idx, province in enumerate(provinces):
                    sub_region_code, sub_region_name = province
                    cell_text = cls._normalize_line(cells[province_idx + 1].get_text(" ", strip=True))
                    numbers = cls._extract_numbers_exact(cell_text, spec["digits"], spec["count"])
                    if len(numbers) != spec["count"]:
                        items = []
                        break

                    for item_order, number_value in enumerate(numbers, start=1):
                        items.append(
                            {
                                "sub_region_code": sub_region_code,
                                "sub_region_name": sub_region_name,
                                "prize_code": prize_code,
                                "prize_order": prize_order,
                                "item_order": item_order,
                                "number_value": number_value,
                            }
                        )
                if not items and prize_order > 0:
                    break

            if items:
                return items

        return []

    @classmethod
    def _parse_mb_from_tables(cls, soup: BeautifulSoup) -> List[Dict]:
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 3:
                continue

            items: List[Dict] = []
            prize_order = 0

            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) < 2:
                    continue

                prize_code = cls._normalize_prize_label(cls._normalize_line(cells[0].get_text(" ", strip=True)))
                if prize_code not in cls.ALLOWED_PRIZES_MB:
                    continue

                spec = cls.MB_PRIZE_SPEC[prize_code]
                cell_text = cls._normalize_line(cells[1].get_text(" ", strip=True))
                numbers = cls._extract_numbers_exact(cell_text, spec["digits"], spec["count"])
                if len(numbers) != spec["count"]:
                    items = []
                    break

                prize_order += 1
                for item_order, number_value in enumerate(numbers, start=1):
                    items.append(
                        {
                            "sub_region_code": "MIENBAC",
                            "sub_region_name": "MIỀN BẮC",
                            "prize_code": prize_code,
                            "prize_order": prize_order,
                            "item_order": item_order,
                            "number_value": number_value,
                        }
                    )

            if items:
                return items

        return []

    @classmethod
    def _resolve_province(cls, text: str) -> Optional[Tuple[str, str]]:
        province_key = cls._province_key(text)
        return cls.PROVINCE_CANONICAL.get(province_key)

    @staticmethod
    def _extract_numbers_exact(text: str, digits: int, expected_count: int) -> List[str]:
        pattern = rf"\b\d{{{digits}}}\b"
        numbers = re.findall(pattern, text)
        if len(numbers) != expected_count:
            return []
        return numbers

    @classmethod
    def _extract_lines(cls, soup: BeautifulSoup) -> List[str]:
        text = soup.get_text(" ", strip=True)
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text)

        boundary_patterns = [
            r"(XSM[NTB]\s+\d{2}/\d{2}/\d{4})",
            r"(XSM[NTB]\s+\d{4}-\d{2}-\d{2})",
            r"(XSM[NTB]\s+\d{2}-\d{2}-\d{4})",
            r"(Giải\b)",
            r"(G\.\s*ĐB)",
            r"(G\.\s*DB)",
            r"(G\.\s*[1-8])",
            r"(Loto\b)",
            r"(Thống kê)",
            r"(Tin tài trợ)",
            r"(QUẢNG CÁO)",
        ]

        for pattern in boundary_patterns:
            text = re.sub(pattern, r"\n\1", text, flags=re.IGNORECASE)

        raw_lines = text.splitlines()

        lines: List[str] = []
        for line in raw_lines:
            normalized = cls._normalize_line(line)
            if normalized:
                lines.append(normalized)
        return lines

    @staticmethod
    def _normalize_line(line: str) -> str:
        line = line.replace("\xa0", " ")
        line = re.sub(r"[ \t]+", " ", line)
        return line.strip()

    @classmethod
    def _find_block_start(cls, lines: List[str], region_code: str, draw_date: str) -> Optional[int]:
        y, m, d = map(int, draw_date.split("-"))
        date_targets = [fmt(y, m, d) for fmt in cls.DATE_FORMATTERS]
        region_token = cls.REGION_PREFIX[region_code]

        for idx, line in enumerate(lines):
            upper_line = cls._ascii_upper(line)
            if region_token not in upper_line:
                continue
            if any(target in line for target in date_targets):
                return idx
        return None

    @classmethod
    def _collect_block_lines(cls, lines: List[str], start_index: int) -> List[str]:
        block: List[str] = []
        for line in lines[start_index + 1:]:
            if cls._is_next_date_heading(line):
                break
            if cls._is_stop_line(line):
                break
            block.append(line)
        return block

    @classmethod
    def _is_next_date_heading(cls, line: str) -> bool:
        upper_line = cls._ascii_upper(line)
        if not re.search(r"\bXSM[NTB]\b", upper_line):
            return False
        return bool(
            re.search(r"\b\d{2}/\d{2}/\d{4}\b", line)
            or re.search(r"\b\d{2}-\d{2}-\d{4}\b", line)
            or re.search(r"\b\d{4}-\d{2}-\d{2}\b", line)
        )

    @classmethod
    def _is_stop_line(cls, line: str) -> bool:
        upper_line = cls._ascii_upper(line)
        return any(keyword in upper_line for keyword in cls.STOP_KEYWORDS)

    @classmethod
    def _parse_mn_mt_block(cls, region_code: str, block_lines: List[str]) -> List[Dict]:
        header_index, provinces = cls._find_header_and_provinces(region_code, block_lines)
        if header_index is None or not provinces:
            return []

        items: List[Dict] = []
        prize_order = 0

        expanded_lines: List[str] = []
        for raw_line in block_lines[header_index + 1:]:
            expanded_lines.extend(cls._split_combined_prize_line(raw_line))

        for line in expanded_lines:
            if cls._is_stop_line(line):
                break

            prize_code = cls._normalize_prize_label(line)
            if prize_code is None or prize_code not in cls.ALLOWED_PRIZES_MN_MT:
                continue

            spec = cls.MN_MT_PRIZE_SPEC[prize_code]
            province_count = len(provinces)

            body = cls._strip_prize_prefix(line)
            digit_stream = re.sub(r"\D", "", body)

            expected_total_numbers = province_count * spec["count"]
            expected_total_digits = expected_total_numbers * spec["digits"]

            if len(digit_stream) != expected_total_digits:
                continue

            all_numbers = cls._chunk_by_digits(digit_stream, spec["digits"])
            if len(all_numbers) != expected_total_numbers:
                continue

            prize_order += 1

            for province_idx, (sub_region_code, sub_region_name) in enumerate(provinces):
                start = province_idx * spec["count"]
                end = start + spec["count"]
                province_numbers = all_numbers[start:end]

                for item_order, number_value in enumerate(province_numbers, start=1):
                    items.append(
                        {
                            "sub_region_code": sub_region_code,
                            "sub_region_name": sub_region_name,
                            "prize_code": prize_code,
                            "prize_order": prize_order,
                            "item_order": item_order,
                            "number_value": number_value,
                        }
                    )

        return items

    @classmethod
    def _split_combined_prize_line(cls, line: str) -> List[str]:
        normalized = cls._normalize_line(line)
        upper_ascii = cls._ascii_upper(normalized).replace("Đ", "D")

        if not upper_ascii.startswith("G.1") and not upper_ascii.startswith("G1"):
            return [normalized]

        match = re.search(r"\s+(ĐB|DB)\s+", normalized, flags=re.IGNORECASE)
        if not match:
            return [normalized]

        left = normalized[: match.start()].strip()
        right = normalized[match.end() :].strip()
        if not left or not right:
            return [normalized]

        return [left, f"G.DB {right}"]

    @classmethod
    def _find_header_and_provinces(
        cls, region_code: str, block_lines: List[str]
    ) -> Tuple[Optional[int], List[Tuple[str, str]]]:
        for idx, line in enumerate(block_lines[:20]):
            upper_ascii = cls._ascii_upper(line)
            if "GIAI" not in upper_ascii:
                continue

            provinces = cls._extract_provinces_from_header_text(line, region_code)
            if provinces:
                return idx, provinces

        for idx, line in enumerate(block_lines[:20]):
            upper_ascii = cls._ascii_upper(line)
            if "GIAI" not in upper_ascii:
                continue

            candidate_lines = [line]
            for j in range(idx + 1, min(idx + 10, len(block_lines))):
                next_line = block_lines[j]

                if cls._normalize_prize_label(next_line):
                    break
                if cls._is_stop_line(next_line):
                    break
                candidate_lines.append(next_line)

            combined = " ".join(candidate_lines)
            provinces = cls._extract_provinces_from_header_text(combined, region_code)
            if provinces:
                last_header_idx = idx + len(candidate_lines) - 1
                return last_header_idx, provinces

        return None, []

    @classmethod
    def _extract_provinces_from_header_text(
        cls, header_text: str, region_code: str
    ) -> List[Tuple[str, str]]:
        normalized_header = cls._compact_ascii(header_text)
        normalized_header = normalized_header.replace("GIAI", "", 1)

        matches: List[Tuple[int, str]] = []
        seen_keys = set()

        for raw_name in cls.REGION_PROVINCES[region_code]:
            compact_name = cls._compact_ascii(raw_name)
            pos = normalized_header.find(compact_name)
            if pos == -1:
                continue

            canonical_key = cls._province_key(raw_name)
            if canonical_key in seen_keys:
                continue

            seen_keys.add(canonical_key)
            matches.append((pos, canonical_key))

        matches.sort(key=lambda item: item[0])

        provinces: List[Tuple[str, str]] = []
        for _, canonical_key in matches:
            if canonical_key not in cls.PROVINCE_CANONICAL:
                continue
            provinces.append(cls.PROVINCE_CANONICAL[canonical_key])

        return provinces

    @classmethod
    def _parse_mb_block(cls, block_lines: List[str]) -> List[Dict]:
        items: List[Dict] = []
        prize_order = 0

        for line in block_lines:
            if cls._is_stop_line(line):
                break

            prize_code = cls._normalize_prize_label(line)
            if prize_code is None or prize_code not in cls.ALLOWED_PRIZES_MB:
                continue

            spec = cls.MB_PRIZE_SPEC[prize_code]
            body = cls._strip_prize_prefix(line)
            digit_stream = re.sub(r"\D", "", body)

            expected_total_digits = spec["count"] * spec["digits"]
            if len(digit_stream) != expected_total_digits:
                continue

            numbers = cls._chunk_by_digits(digit_stream, spec["digits"])
            if len(numbers) != spec["count"]:
                continue

            prize_order += 1

            for item_order, number_value in enumerate(numbers, start=1):
                items.append(
                    {
                        "sub_region_code": "MIENBAC",
                        "sub_region_name": "MIỀN BẮC",
                        "prize_code": prize_code,
                        "prize_order": prize_order,
                        "item_order": item_order,
                        "number_value": number_value,
                    }
                )

        return items

    @classmethod
    def _normalize_prize_label(cls, line: str) -> Optional[str]:
        upper_ascii = cls._ascii_upper(line).replace("Đ", "D")
        compact = re.sub(r"[^A-Z0-9]", "", upper_ascii)

        if compact.startswith("GDB"):
            return "DB"

        m = re.match(r"^G([1-8])", compact)
        if m:
            return f"G{m.group(1)}"

        return None

    @classmethod
    def _strip_prize_prefix(cls, line: str) -> str:
        upper_ascii = cls._ascii_upper(line).replace("Đ", "D")
        stripped = re.sub(r"^\s*G\s*\.?\s*(DB|[1-8])", "", upper_ascii, count=1)
        return stripped.strip()

    @staticmethod
    def _chunk_by_digits(digit_stream: str, size: int) -> List[str]:
        if size <= 0:
            return []
        if len(digit_stream) % size != 0:
            return []
        return [digit_stream[i:i + size] for i in range(0, len(digit_stream), size)]

    @staticmethod
    def _ascii_upper(text: str) -> str:
        norm = unicodedata.normalize("NFD", text)
        no_accents = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
        return no_accents.upper()

    @classmethod
    def _compact_ascii(cls, text: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", cls._ascii_upper(text).replace("Đ", "D"))

    @classmethod
    def _province_key(cls, raw_name: str) -> str:
        key = cls._compact_ascii(raw_name)
        if key == "TTHUE":
            return "THUATHIENHUE"
        return key
