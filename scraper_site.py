import requests
from bs4 import BeautifulSoup
import re
import time

WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2-yZrItc5cO-aCt"

SEARCH_QUERY = 'site:instagram.com ("ارسال به سراسر کشور" OR "سفارش دایرکت") ("تهران" OR "کرج") "09"'
GOOGLE_SEARCH_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&num=10"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def extract_phone_numbers(text):
    pattern = r'(?:09|\+?989|00989)\d{9}'
    return list(set(re.findall(pattern, text.replace(" ", "").replace("-", ""))))

def run_scraper():
    print("شروع جستجوی لید (کمپین سایت)...")
    try:
        response = requests.get(GOOGLE_SEARCH_URL, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        print("خطا: زمان پاسخگویی گوگل به پایان رسید (Timeout).")
        return
    except Exception as e:
        print(f"خطا در اتصال: {e}")
        return

    if response.status_code != 200:
        print(f"کد وضعیت نامعتبر از گوگل: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    for result in soup.select('div.g'):
        link_tag = result.find('a', href=True)
        snippet_tag = result.find('div', class_=['VwiC3b', 'yXK7lf', 'IsZvec'])
        
        if link_tag and "instagram.com" in link_tag['href']:
            ig_url = link_tag['href']
            snippet_text = snippet_tag.text if snippet_tag else "پیج اینستاگرام"
            page_name = ig_url.rstrip('/').split('/')[-1]
            phones = extract_phone_numbers(snippet_text)
            
            if phones:
                data = {
                    "name": f"پیج {page_name}",
                    "instagram": ig_url,
                    "phone": phones[0],
                    "details": snippet_text,
                    "campaign": "metapage_site"
                }
                try:
                    requests.post(WP_API_URL, json=data, headers={"Content-Type": "application/json", "X-API-TOKEN": API_TOKEN}, timeout=10)
                except Exception:
                    pass
                time.sleep(2)

if __name__ == "__main__":
    run_scraper()
