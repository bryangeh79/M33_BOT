from pprint import pprint

from src.modules.result.services.result_fetch_service import ResultFetchService
from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.result.repositories.draw_result_items_repository import DrawResultItemsRepository


def main():
    draw_date = "2026-03-17"
    region_group = "MN"

    fetch_service = ResultFetchService()
    results_repo = DrawResultsRepository()
    items_repo = DrawResultItemsRepository()

    refresh_result = fetch_service.fetch_and_store(draw_date, region_group)
    print("=== fetch_and_store result ===")
    pprint(refresh_result)

    row = results_repo.get_result(draw_date, region_group)
    print("\n=== draw_results row after refresh ===")
    pprint(row)

    if row:
        items = items_repo.find_by_draw_result_id(row["id"])
        print("\n=== items count after refresh ===")
        print(len(items))
        print("\n=== first 20 items ===")
        pprint(items[:20])


if __name__ == "__main__":
    main()