import requests
from bs4 import BeautifulSoup
import re
import time

WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2-yZrItc5cO-aCt" # توکن خودتان را اینجا قرار دهید

SEARCH_QUERY = 'site:instagram.com "تهران" "09"'
GOOGLE_SEARCH_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&num=5"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def run_scraper():
    print("شروع اجرای اسکریپت و ارسال لید تست گیت‌هاب...")

    # ۱. ارسال یک لید تستی حتمی برای اطمینان از برقراری ارتباط گیت‌هاب و وردپرس
    test_lead = {
        "name": "مشتری تستی از گیت‌هاب",
        "instagram": "https://instagram.com/test_github_client",
        "phone": "09123456789",
        "details": "این لید به صورت اتوماتیک از طرف ربات گیت‌هاب ارسال شده است.",
        "campaign": "metapage_site"
    }

    try:
        print("در حال ارسال لید تستی به وردپرس...")
        res = requests.post(WP_API_URL, json=test_lead, headers={"Content-Type": "application/json", "X-API-TOKEN": API_TOKEN}, timeout=10)
        print(f"پاسخ وردپرس به لید تستی: {res.status_code} - {res.text}")
    except Exception as ex:
        print(f"خطا در ارسال لید تستی: {ex}")

    # ۲. تلاش برای جستجو در گوگل (بدون توقف در صورت خطا)
    try:
        response = requests.get(GOOGLE_SEARCH_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for result in soup.select('div.g'):
                link_tag = result.find('a', href=True)
                snippet_tag = result.find('div', class_=['VwiC3b', 'yXK7lf', 'IsZvec'])
                if link_tag and "instagram.com" in link_tag['href']:
                    url = link_tag['href']
                    snippet_text = snippet_tag.text if snippet_tag else "یافت شده از گوگل"
                    page_name = url.rstrip('/').split('/')[-1]
                    phone_match = re.search(r'(?:09|\+?989|00989)\d{9}', snippet_text.replace(" ", ""))
                    
                    if phone_match:
                        data = {
                            "name": f"پیج {page_name}",
                            "instagram": url,
                            "phone": phone_match.group(0),
                            "details": snippet_text,
                            "campaign": "metapage_site"
                        }
                        requests.post(WP_API_URL, json=data, headers={"Content-Type": "application/json", "X-API-TOKEN": API_TOKEN}, timeout=10)
                        time.sleep(1)
    except Exception:
        print("جستجوی گوگل در این لحظه محدود بود، اما تست اصلی انجام شد.")

    print("پایان اجرای اسکریپت.")

if __name__ == "__main__":
    run_scraper()
