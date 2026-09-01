import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytz
import pytesseract
from PIL import Image
from io import BytesIO
import re

def extract_all_prizes_via_ocr():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today = now.strftime('%Y-%m-%d')

    if now.hour < 15: draw_time = "1:00 PM"
    elif now.hour < 19: draw_time = "6:00 PM"
    else: draw_time = "8:00 PM"

    print(f"Starting OCR Extraction for Date: {today}, Time: {draw_time}")
    prizes = {"1st": "Pending", "2nd": "Pending", "3rd": "Pending", "4th": "Pending", "5th": "Pending"}

    try:
        url = "https://dear-lottery.in/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        img_tag = soup.find('img', src=re.compile(r'.*result.*\.jpg', re.IGNORECASE))

        if img_tag and img_tag.get('src'):
            img_url = img_tag['src']
            if not img_url.startswith('http'):
                img_url = "https://dear-lottery.in" + img_url

            print("Downloading Image for OCR:", img_url)
            img_response = requests.get(img_url)
            img = Image.open(BytesIO(img_response.content))
            extracted_text = pytesseract.image_to_string(img)

            first_prize_match = re.search(r'[0-9]{2}[A-Z]\s?[0-9]{5}', extracted_text)
            if first_prize_match: prizes["1st"] = first_prize_match.group()

            four_digits = re.findall(r'\b[0-9]{4}\b', extracted_text)
            if len(four_digits) > 10:
                prizes["2nd"] = " | ".join(four_digits[0:10])
                prizes["3rd"] = " | ".join(four_digits[10:20])
                prizes["4th"] = " | ".join(four_digits[20:30])
                prizes["5th"] = " | ".join(four_digits[30:80])

    except Exception as e:
        print("Scraping ya OCR me Error:", e)

    new_data = pd.DataFrame([{
        'Date': today, 
        'Time': draw_time, 
        '1st_Prize': prizes["1st"],
        '2nd_Prize': prizes["2nd"],
        '3rd_Prize': prizes["3rd"],
        '4th_Prize': prizes["4th"],
        '5th_Prize': prizes["5th"]
    }])

    new_data.to_csv('lottery_data.csv', mode='a', header=False, index=False)
    print("All prizes saved successfully!")

if __name__ == "__main__":
    extract_all_prizes_via_ocr()

