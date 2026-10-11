import os
import smtplib
import requests
import re
from email.mime.text import MIMEText

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
MIN_VACANCY = 3

TARGET_URL = "https://gozasoro.rsvsys.jp/reservations/calendar?date=2026/11/22"
TARGET_DATES = ["2026/11/22", "2026/11/23"]

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

def extract_vacancy_by_date(html, target_date):
    # data-date="2026/11/22"を含む要素から残名数を取得
    pattern = rf'data-date="{re.escape(target_date)}"[^>]*data-stock="(\d+)"'
    matches = re.findall(pattern, html)
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

    for target_date in TARGET_DATES:
        print(f"\n--- {target_date} の確認 ---")
        vacancies = extract_vacancy_by_date(html, target_date)
        print(f"取得した空き状況：{vacancies}")

        if not vacancies:
            print("空き情報が取得できませんでした（満員または予約枠なし）")
            continue

        for v in vacancies:
            if int(v) >= MIN_VACANCY:
                print(f"{v}名様の空きを検知！メールを送信します。")
                notify(
                    f"【速報】御座候ミュージアム{target_date}に{v}名様の空きがあります！",
                    f"{target_date}に{v}名様の空きが出ました！今すぐ予約してください。\n\nhttps://gozasoro.rsvsys.jp/reservations/calendar"
                )
                break
        else:
            print(f"空きなし（現在の状況：{vacancies}）")

if __name__ == "__main__":
    main()
