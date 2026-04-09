from pprint import pprint

from src.modules.result.services.result_fetch_service import ResultFetchService
from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.result.repositories.draw_result_items_repository import (
    DrawResultItemsRepository,
)


def main():
    draw_date = "2026-03-17"
    region_code = "MN"

    fetch_service = ResultFetchService()
    results_repo = DrawResultsRepository()
    items_repo = DrawResultItemsRepository()

    print("\n=== STEP 1: FETCH ===")
    fetch_result = fetch_service.fetch_and_store(draw_date, region_code)
    pprint(fetch_result)

    print("\n=== STEP 2: CHECK DRAW RESULT ===")
    draw_result = results_repo.get_result(draw_date, region_code)
    pprint(draw_result)

    print("\n=== STEP 3: CHECK ITEMS ===")
    if draw_result:
        items = items_repo.find_by_draw_result_id(draw_result["id"])
        print(f"items count = {len(items)}")
        pprint(items[:10])


if __name__ == "__main__":
    main()