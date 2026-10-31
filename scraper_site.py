import requests
from bs4 import BeautifulSoup
import re
import time

WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2-yZrItc5cO-aCt"

# جستجوی آزادتر در گوگل برای پیدا کردن اینستاگرام یا تلگرام کسب‌وکارها در تهران
SEARCH_QUERY = 'site:instagram.com OR site:t.me "تهران" ("سفارش" OR "خدمات" OR "ارسال")'
GOOGLE_SEARCH_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&num=10"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def run_scraper():
    print("شروع جستجوی آزاد لید در گوگل...")
    try:
        response = requests.get(GOOGLE_SEARCH_URL, headers=headers, timeout=10)
    except Exception as e:
        print(f"خطا در اتصال به گوگل: {e}")
        return

    if response.status_code != 200:
        print(f"کد وضعیت گوگل: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    results_found = 0

    for result in soup.select('div.g'):
        link_tag = result.find('a', href=True)
        snippet_tag = result.find('div', class_=['VwiC3b', 'yXK7lf', 'IsZvec'])
        
        if link_tag:
            url = link_tag['href']
            # بررسی اینکه لینک مربوط به اینستاگرام یا تلگرام باشد
            if "instagram.com" in url or "t.me" in url:
                snippet_text = snippet_tag.text if snippet_tag else "یافت شده از جستجوی گوگل"
                page_name = url.rstrip('/').split('/')[-1]
                
                # استخراج شماره موبایل اگر وجود داشته باشد، در غیر این صورت یک شماره پیش‌فرض تست قرار می‌دهیم
                phone_match = re.search(r'(?:09|\+?989|00989)\d{9}', snippet_text.replace(" ", ""))
                phone = phone_match.group(0) if phone_match else "09120000000" # شماره پیش‌فرض برای تست ورود لید
                
                data = {
                    "name": f"لیدِ {page_name}",
                    "instagram": url if "instagram.com" in url else "https://instagram.com/tele_lead",
                    "phone": phone,
                    "details": snippet_text,
                    "campaign": "metapage_site"
                }
                
                print(f"در حال ارسال لید: {url} ...")
                try:
                    res = requests.post(WP_API_URL, json=data, headers={"Content-Type": "application/json", "X-API-TOKEN": API_TOKEN}, timeout=10)
                    print(f"پاسخ وردپرس: {res.text}")
                    results_found += 1
                except Exception as ex:
                    print(f"خطا در ارسال به وردپرس: {ex}")
                
                time.sleep(2)

    print(f"پایان جستجو. تعداد {results_found} لید پردازش شد.")

if __name__ == "__main__":
    run_scraper()
