import requests
from bs4 import BeautifulSoup
import re
import time

# تنظیمات اتصال به سایت متاپیج
WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "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"

# تنظیمات جستجو (مثلاً پیدا کردن سالن‌های زیبایی در تهران که پیج اینستاگرام دارند)
SEARCH_QUERY = 'site:instagram.com "تهران" "سالن زیبایی" "09"'
GOOGLE_SEARCH_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&num=20"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def extract_phone_numbers(text):
    # الگوی یافتن شماره موبایل‌های ایرانی
    pattern = r'(?:09|\+?989|00989)\d{9}'
    matches = re.findall(pattern, text.replace(" ", "").replace("-", ""))
    return list(set(matches))

def send_lead_to_wordpress(name, ig_url, phone, bio_text):
    data = {
        "name": name,
        "instagram": ig_url,
        "phone": phone,
        "details": bio_text
    }
    
    req_headers = {
        "Content-Type": "application/json",
        "X-API-TOKEN": API_TOKEN
    }
    
    response = requests.post(WP_API_URL, json=data, headers=req_headers)
    print(f"ارسال به وردپرس: {ig_url} | پاسخ سرور: {response.text}")

def run_scraper():
    print("شروع جستجو در گوگل...")
    response = requests.get(GOOGLE_SEARCH_URL, headers=headers)
    
    if response.status_code != 200:
        print("خطا در دریافت نتایج گوگل")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='g')

    for result in search_results:
        link_tag = result.find('a', href=True)
        snippet_tag = result.find('div', class_='VwiC3b') # کلاس توضیحات گوگل (ممکن است تغییر کند)
        
        if link_tag and snippet_tag and "instagram.com" in link_tag['href']:
            ig_url = link_tag['href']
            snippet_text = snippet_tag.text
            
            # استخراج نام پیج از URL
            page_name = ig_url.rstrip('/').split('/')[-1]
            
            # پیدا کردن شماره‌ها در توضیحات ایندکس شده
            phones = extract_phone_numbers(snippet_text)
            
            if phones:
                # ارسال اولین شماره پیدا شده به وردپرس
                send_lead_to_wordpress(f"پیج {page_name}", ig_url, phones[0], snippet_text)
                time.sleep(2) # وقفه برای جلوگیری از فشار به سرور

if __name__ == "__main__":
    run_scraper()
