import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytz
import pytesseract
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
import re

def extract_all_prizes_via_ocr():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today = now.strftime('%Y-%m-%d')
    
    if now.hour < 15: draw_time = "1:00 PM"
    elif now.hour < 19: draw_time = "6:00 PM"
    else: draw_time = "8:00 PM"

    print(f"Starting Multi-Source OCR Extraction for Date: {today}, Time: {draw_time}")
    prizes = {"1st": "Pending", "2nd": "Pending", "3rd": "Pending", "4th": "Pending", "5th": "Pending"}

    # 3 Behtareen Reliable Websites ki List (Backup ke sath)
    urls = [
        "https://lottery.sambad.com/",
        "https://sambad.com/",
        "https://dearlottery.in/"
    ]

    success = False
    for url in urls:
        if success:
            break
        try:
            print(f"Trying source: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Result image ya banner dhundhna
            img_tag = soup.find('img', src=re.compile(r'.*(result|dear|jpg|png).*', re.IGNORECASE))
            
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                if not img_url.startswith('http'):
                    img_url = urljoin(url, img_url)
                
                print(f"Downloading Image from: {img_url}")
                img_response = requests.get(img_url, timeout=15)
                
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content))
                    extracted_text = pytesseract.image_to_string(img)
                    
                    # 1st Prize Extraction (eg. 36G 09511)
                    first_prize_match = re.search(r'[0-9]{2}[A-Z]\s?[0-9]{5}', extracted_text)
                    if first_prize_match: 
                        prizes["1st"] = first_prize_match.group()
                    
                    # 2nd, 3rd, 4th, 5th Prize Extraction (4-digit numbers)
                    four_digits = re.findall(r'\b[0-9]{4}\b', extracted_text)
                    if len(four_digits) > 10:
                        prizes["2nd"] = " | ".join(four_digits[0:10])
                        prizes["3rd"] = " | ".join(four_digits[10:20])
                        prizes["4th"] = " | ".join(four_digits[20:30])
                        prizes["5th"] = " | ".join(four_digits[30:80])
                    
                    success = True
                    print("OCR Extraction Successful from:", url)
                    break
                    
        except Exception as e:
            print(f"Failed with {url} due to error: {e}")

    # CSV file me data save karna
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
    print("All prizes processed and saved successfully!")

if __name__ == "__main__":
    extract_all_prizes_via_ocr()
