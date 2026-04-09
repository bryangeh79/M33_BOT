import httpx
from datetime import date

def test_urls():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 测试旧的 MT URL 结构
    old_urls = [
        "https://xosodaiphat.com/xsmt-cn.html",  # 周日
        "https://xosodaiphat.com/xsmt-thu-7.html",  # 周六
        "https://xosodaiphat.com/xsmt-thu-6.html",  # 周五
        "https://xosodaiphat.com/xsmt-thu-5.html",  # 周四
        "https://xosodaiphat.com/xsmt-thu-4.html",  # 周三
        "https://xosodaiphat.com/xsmt-thu-3.html",  # 周二
        "https://xosodaiphat.com/xsmt-thu-2.html",  # 周一
    ]
    
    print("Testing old MT URLs:")
    for url in old_urls:
        try:
            with httpx.Client(timeout=10, headers=headers) as client:
                resp = client.get(url, follow_redirects=False)
                print(f"  {url}: {resp.status_code} -> {resp.headers.get('location', 'N/A')}")
        except Exception as e:
            print(f"  {url}: ERROR - {e}")
    
    print("\nTesting main pages:")
    main_urls = [
        "https://xosodaiphat.com/xsmn-xo-so-mien-nam.html",
        "https://xosodaiphat.com/xsmt-xo-so-mien-trung.html", 
        "https://xosodaiphat.com/xsmb-xo-so-mien-bac.html",
    ]
    
    for url in main_urls:
        try:
            with httpx.Client(timeout=10, headers=headers) as client:
                resp = client.get(url, follow_redirects=False)
                print(f"  {url}: {resp.status_code}")
                if resp.status_code == 200:
                    # 检查页面中是否有日期信息
                    if "KQXS" in resp.text[:2000]:
                        print(f"    Contains KQXS (likely valid)")
                elif resp.status_code in [301, 302]:
                    print(f"    Redirects to: {resp.headers.get('location', 'N/A')}")
        except Exception as e:
            print(f"  {url}: ERROR - {e}")

if __name__ == "__main__":
    test_urls()