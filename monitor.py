import os
import smtplib
import requests
import re
from email.mime.text import MIMEText

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
TARGET_URL = "https://gozasoro.rsvsys.jp/reservations/calendar"
TARGET_DATES = ["11/22", "11/23"]
MIN_VACANCY = 3

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers, timeout=30)
    print(f"ステータスコード：{response.status_code}")
    return response.text

def extract_vacancy(html):
    matches = re.findall(r'残<i>(\d+)名様</i>', html)
    print(f"取得した空き状況：{matches}")
    return matches

def notify(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        s.send_message(msg)

def main():
    try:
        html = fetch(TARGET_URL)
    except Exception as e:
        print(f"取得エラー：{e}")
        return

    vacancies = extract_vacancy(html)

    if not vacancies:
        print("空き情報が取得できませんでした")
        return

    for v in vacancies:
        if int(v) >= MIN_VACANCY:
            print(f"{v}名様の空きを検知！メールを送信します。")
            notify(
                f"【速報】御座候ミュージアムに{v}名様の空きがあります！",
                f"11/22または11/23に{v}名様の空きが出ました！今すぐ予約してください。\n\n{TARGET_URL}"
            )
            return

    print(f"空きなし（現在の状況：{vacancies}）")

if __name__ == "__main__":
    main()
