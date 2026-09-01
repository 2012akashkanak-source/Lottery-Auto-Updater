import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytz
import re

def fetch_lottery_data():
    # India ka time set karna
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    today_date = now.strftime('%Y-%m-%d')
    current_hour = now.hour

    # Time ke hisab se draw decide karna
    if current_hour < 15:
        draw_time = "1:00 PM"
    elif current_hour < 19:
        draw_time = "6:00 PM"
    else:
        draw_time = "8:00 PM"

    print(f"Checking result for Date: {today_date}, Time: {draw_time}")

    try:
        # Nagaland lottery ki dummy scraping logic
        # (Baad me isko real API ya PDF OCR se replace karenge)
        url = "https://dear-lottery.in/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_data = soup.get_text()

        # First prize ka pattern dhundhna (eg: 36G 09511)
        winning_numbers = re.findall(r'[0-9]{2}[A-L]\s[0-9]{5}', text_data)

        if winning_numbers:
            first_prize = winning_numbers[0]
        else:
            first_prize = "Pending"

        # Data ko CSV me daalna
        new_data = pd.DataFrame({'Date': [today_date], 'Time': [draw_time], '1st_Prize': [first_prize]})
        new_data.to_csv('lottery_data.csv', mode='a', header=False, index=False)
        print(f"Success! Saved Data: {first_prize}")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    fetch_lottery_data()
