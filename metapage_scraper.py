import requests
from bs4 import BeautifulSoup
import re
import time

# تنظیمات اتصال به وردپرس
WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2"

# انتخاب نوع کمپین هدف برای این دور از جستجو:
# گزینه‌ها: 'metapage_site' | 'behapp_3dviewer' | 'ads_billboard' | 'meta_global_expo'
TARGET_CAMPAIGN = 'behapp_3dviewer'

# تنظیمات جستجو بر اساس کمپین
if TARGET_CAMPAIGN == 'behapp_3dviewer':
    SEARCH_QUERY = 'site:instagram.com "معمار" OR "طراح داخلی" "تهران" "09"'
elif TARGET_CAMPAIGN == 'ads_billboard':
    SEARCH_QUERY = 'site:instagram.com "آژانس تبلیغاتی" OR "برندینگ" "تهران" "09"'
else:
    SEARCH_QUERY = 'site:instagram.com "سالن زیبایی" OR "کلینیک" "تهران" "09"'

GOOGLE_SEARCH_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&num=20"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_phone_numbers(text):
    pattern = r'(?:09|\+?989|00989)\d{9}'
    matches = re.findall(pattern, text.replace(" ", "").replace("-", ""))
    return list(set(matches))

def send_lead_to_wordpress(name, ig_url, phone, bio_text, campaign_type):
    data = {
        "api_token": API_TOKEN,
        "name": name,
        "instagram": ig_url,
        "phone": phone,
        "details": bio_text,
        "campaign": campaign_type
    }

    req_headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": API_TOKEN
    }

    try:
        response = requests.post(WP_API_URL, json=data, headers=req_headers, timeout=20)
        print(f"ارسال به وردپرس: {ig_url} | کد: {response.status_code} | پاسخ: {response.text}")
    except Exception as e:
        print(f"خطا در ارسال به وردپرس: {e}")

def run_scraper():
    print(f"شروع جستجو در گوگل برای کمپین: {TARGET_CAMPAIGN} ...")
    try:
        response = requests.get(GOOGLE_SEARCH_URL, headers=headers, timeout=15)
    except Exception as e:
        print(f"خطا در اتصال به گوگل: {e}")
        return

    if response.status_code != 200:
        print(f"خطا در دریافت نتایج گوگل. کد وضعیت: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.select('div.g')

    if not search_results:
        print("هیچ نتیجه‌ای یافت نشد یا ساختار صفحه گوگل تغییر کرده است.")
        return

    found_count = 0
    for result in search_results:
        link_tag = result.find('a', href=True)
        snippet_tag = result.find('div', class_=['VwiC3b', 'yXK7lf', 'IsZvec'])

        if link_tag and "instagram.com" in link_tag['href']:
            ig_url = link_tag['href']
            snippet_text = snippet_tag.text if snippet_tag else "اطلاعات پیش‌فرض پیج اینستاگرام"
            page_name = ig_url.rstrip('/').split('/')[-1]
            phones = extract_phone_numbers(snippet_text)

            if phones:
                send_lead_to_wordpress(f"پیج {page_name}", ig_url, phones[0], snippet_text, TARGET_CAMPAIGN)
                found_count += 1
                time.sleep(3)

    print(f"پایان جستجو. تعداد {found_count} لید جدید پردازش شد.")

if __name__ == "__main__":
    run_scraper()
