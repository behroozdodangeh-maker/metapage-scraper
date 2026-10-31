import requests

url = "https://chat.metapageiran.ir/wp-json/metapage/v1/add-lead"
headers = {
    "Content-Type": "application/json",
    "X-API-TOKEN": "FAd6fLyVSgHXRgVxT3BlbkFJOe24MdYjQkCYGazR928XkTg5om4yT7Cc2-yZrItc5cO-aCt" # همان توکن تنظیمات وردپرس
}
data = {
    "name": "تست دستی از بیرون",
    "instagram": "https://instagram.com/test_page",
    "phone": "09123456789",
    "details": "این یک تست برای بررسی ارتباط گیت‌هاب و وردپرس است.",
    "campaign": "behapp_3dviewer"
}

response = requests.post(url, json=data, headers=headers)
print("کد وضعیت:", response.status_code)
print("پاسخ سرور:", response.text)
