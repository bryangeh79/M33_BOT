from datetime import date

from src.modules.schedule.constants.region_schedule_map import get_allowed_regions


def test_friday_mn_regions_match_live_draw_order():
    # 2026-04-10 is Friday. Live draw set for MN should be:
    # Binh Duong, Tra Vinh, Vinh Long.
    allowed = get_allowed_regions(date(2026, 4, 10), "MN")
    assert allowed == ["bd", "tv", "vl"]


def test_sunday_mt_regions_include_hue():
    # 2026-04-12 is Sunday. MT should include Kon Tum, Khanh Hoa, Hue.
    allowed = get_allowed_regions(date(2026, 4, 12), "MT")
    assert allowed == ["kt", "kh", "tth"]


if __name__ == "__main__":
    test_friday_mn_regions_match_live_draw_order()
    test_sunday_mt_regions_include_hue()
    print("OK")
