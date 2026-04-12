from src.modules.settlement.constants.region_aliases import normalize_region_alias


def test_mn_dl_maps_to_dalat():
    assert normalize_region_alias("dl", "MN") == "DALAT"


if __name__ == "__main__":
    test_mn_dl_maps_to_dalat()
    print("OK")
