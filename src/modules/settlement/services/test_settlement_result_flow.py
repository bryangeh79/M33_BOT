from pprint import pprint

from src.modules.result.providers.xosodaiphat_provider import XosodaiphatProvider
from src.modules.result.parsers.xosodaiphat_result_parser import XosodaiphatResultParser


def main():
    draw_date = "2026-03-17"
    region_code = "MN"

    provider_result = XosodaiphatProvider.fetch_raw_html(region_code, draw_date)
    html = provider_result["html"]

    items = XosodaiphatResultParser.parse(region_code, draw_date, html)

    print("\n=== parsed items count ===")
    print(len(items))

    print("\n=== first 20 parsed items ===")
    pprint(items[:20])


if __name__ == "__main__":
    main()