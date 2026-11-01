import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import unquote

WP_API_URL = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
API_TOKEN = "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2"
CAMPAIGN = "meta_global_expo"

QUERIES = [
    'site:instagram.com "استارتاپ" "تهران" "09"',
    'site:instagram.com "کلینیک زیبایی" "تهران" "0912"',
    'site:instagram.com "فروشگاه اینترنتی" "0912"'
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7"
}

def normalize_digits(text):
    persian = "۰۱۲۳۴۵۶۷۸۹"
    arabic = "٠١٢٣٤٥٦٧٨٩"
    english = "0123456789"
    trans = str.maketrans(persian + arabic, english * 2)
    return text.translate(trans)

def extract_phone_numbers(text):
    clean_text = normalize_digits(text).replace(" ", "").replace("-", "").replace("_", "")
    pattern = r'(?:09|\+?989|00989)\d{9}'
    return list(set(re.findall(pattern, clean_text)))

def extract_ig_username(url):
    url = unquote(url)
    match = re.search(r'instagram\.com/([a-zA-Z0-9._]+)', url)
    if match:
        username = match.group(1)
        if username not in ['p', 'reel', 'tv', 'explore', 'stories', 'accounts']:
            return username
    return None

def search_web(query):
    results = []
    try:
        resp = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for item in soup.select('.result'):
                a_tag = item.select_one('.result__a')
                snippet_tag = item.select_one('.result__snippet')
                if a_tag and snippet_tag:
                    results.append((a_tag.get('href', ''), a_tag.text + " " + snippet_tag.text))
    except Exception as e:
        print(f"خطا در DuckDuckGo: {e}")

    if not results:
        try:
            resp = requests.get("https://search.yahoo.com/search", params={"p": query, "n": 20}, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for item in soup.select('div.algo'):
                    a_tag = item.find('a', href=True)
                    if a_tag:
                        results.append((a_tag['href'], item.get_text(" ", strip=True)))
        except Exception as e:
            print(f"خطا در Yahoo: {e}")

    return results

def run_scraper():
    print(f"=== شروع جستجوی لید برای کمپین: {CAMPAIGN} ===")
    total_sent = 0

    for query in QUERIES:
        print(f"\nدر حال جستجوی عبارت: {query}")
        items = search_web(query)
        print(f"تعداد نتایج اولیه یافت‌شده: {len(items)}")

        for raw_url, text_content in items:
            username = extract_ig_username(raw_url)
            if not username:
                continue

            ig_url = f"https://www.instagram.com/{username}/"
            phones = extract_phone_numbers(text_content)

            if phones:
                phone = phones[0]
                print(f"-> لید پیدا شد: @{username} | شماره: {phone}")
                data = {
                    "api_token": API_TOKEN,
                    "name": f"پیج {username}",
                    "instagram": ig_url,
                    "phone": phone,
                    "details": text_content[:300],
                    "campaign": CAMPAIGN
                }
                try:
                    res = requests.post(
                        WP_API_URL,
                        json=data,
                        headers={"Content-Type": "application/json", "X-API-TOKEN": API_TOKEN},
                        timeout=25
                    )
                    print(f"   پاسخ وردپرس (کد {res.status_code}): {res.text}")
                    if res.status_code == 200:
                        total_sent += 1
                except Exception as e:
                    print(f"   خطا در ارسال به وردپرس: {e}")
                time.sleep(2)

        time.sleep(3)

    print(f"\n=== پایان عملیات. مجموع لیدهای ارسال‌شده به وردپرس: {total_sent} ===")

if __name__ == "__main__":
    run_scraper()
