import httpx
from datetime import date as _date


class XosodaiphatProvider:
    """
    Provider responsible for downloading raw HTML from xosodaiphat.com.
    """

    BASE_URLS = {
        "MN": "https://xosodaiphat.com/xsmn-xo-so-mien-nam.html",
        "MT": "https://xosodaiphat.com/xsmt-xo-so-mien-trung.html",
        "MB": "https://xosodaiphat.com/xsmb-xo-so-mien-bac.html",
    }

    # MT weekday page slugs: Python weekday() 0=Mon … 6=Sun
    MT_WEEKDAY_SLUGS = {
        0: "thu-2",
        1: "thu-3",
        2: "thu-4",
        3: "thu-5",
        4: "thu-6",
        5: "thu-7",
        6: "cn",
    }

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )

    @classmethod
    def validate_region(cls, region_code: str):
        """
        Validate region code.
        """
        if region_code not in cls.BASE_URLS:
            raise ValueError(f"Unsupported region code: {region_code}")

    @classmethod
    def build_url(cls, region_code: str, draw_date: str) -> str:
        """
        Build the source URL for the given region and date.

        MT uses weekday-specific pages (e.g. xsmt-thu-5.html) to get
        today's results directly, avoiding stale data on the main page.
        MN and MB use the main page; parser filters by date.
        
        NOTE: If xsmt-{weekday}.html returns 301, fallback to main page.
        """
        cls.validate_region(region_code)

        if region_code == "MT":
            d = _date.fromisoformat(draw_date)
            slug = cls.MT_WEEKDAY_SLUGS[d.weekday()]
            weekday_url = f"https://xosodaiphat.com/xsmt-{slug}.html"
            
            # Test if weekday URL works, if not fallback to main page
            try:
                import httpx
                headers = {"User-Agent": cls.USER_AGENT}
                with httpx.Client(timeout=5, headers=headers) as client:
                    resp = client.get(weekday_url, follow_redirects=False)
                    if resp.status_code == 200:
                        return weekday_url
                    # If redirects to 404 or other error, use main page
                    print(f"MT weekday URL {weekday_url} returned {resp.status_code}, using main page")
            except Exception as e:
                print(f"Error testing MT weekday URL: {e}, using main page")
            
            # Fallback to main MT page
            return cls.BASE_URLS[region_code]

        return cls.BASE_URLS[region_code]

    @classmethod
    def fetch_raw_html(cls, region_code: str, draw_date: str) -> dict:
        """
        Fetch raw HTML for the given region and draw date.

        Returns:
        {
            "source_url": str,
            "html": str
        }
        """
        url = cls.build_url(region_code, draw_date)

        headers = {
            "User-Agent": cls.USER_AGENT,
        }

        with httpx.Client(timeout=30, headers=headers, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Check if we got redirected to a 404 page
            final_url = str(response.url)
            if "404" in final_url or "not-found" in final_url.lower():
                raise httpx.HTTPStatusError(
                    f"URL redirected to 404 page: {final_url}",
                    request=response.request,
                    response=response
                )

        return {
            "source_url": url,
            "html": response.text,
        }