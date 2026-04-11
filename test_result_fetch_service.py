from src.modules.result.services.result_fetch_service import ResultFetchService
from src.modules.result.parsers.xosodaiphat_result_parser import XosodaiphatResultParser


def build_mn_item(sub_region_code: str, prize_code: str, item_order: int, number_value: str, prize_order: int):
    return {
        "sub_region_code": sub_region_code,
        "sub_region_name": sub_region_code,
        "prize_code": prize_code,
        "prize_order": prize_order,
        "item_order": item_order,
        "number_value": number_value,
    }


def build_complete_mn_items(subregions: list[str]) -> list[dict]:
    service = ResultFetchService()
    items: list[dict] = []
    prize_order = 0

    for prize_code, spec in service.EXPECTED_PRIZE_SPECS["MN"].items():
        prize_order += 1
        digits = int(spec["digits"])
        count = int(spec["count"])
        for subregion_index, subregion in enumerate(subregions, start=1):
            for item_order in range(1, count + 1):
                number_value = str((subregion_index * 100000 + prize_order * 100 + item_order) % (10 ** digits)).zfill(digits)
                items.append(
                    build_mn_item(
                        sub_region_code=subregion,
                        prize_code=prize_code,
                        item_order=item_order,
                        number_value=number_value,
                        prize_order=prize_order,
                    )
                )
    return items


def test_mn_result_allows_four_subregions_on_saturday():
    service = ResultFetchService()
    items = build_complete_mn_items(["TPHCM", "LONGAN", "BINHPHUOC", "HAUGIANG"])
    assert service._is_items_complete("MN", items) is True


def test_parser_splits_combined_g1_db_line():
    lines = XosodaiphatResultParser._split_combined_prize_line(
        "G.1 03769 95720 82303 95985 ĐB 812128 169749 307467 104888"
    )
    assert lines == [
        "G.1 03769 95720 82303 95985",
        "G.DB 812128 169749 307467 104888",
    ]


if __name__ == "__main__":
    test_mn_result_allows_four_subregions_on_saturday()
    test_parser_splits_combined_g1_db_line()
    print("OK")
