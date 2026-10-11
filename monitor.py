import os
import smtplib
import requests
import re
from email.mime.text import MIMEText

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
MIN_VACANCY = 3

# 監視する日付と週のURLを指定
TARGETS = [
    {
        "date": "11/22",
        "url": "https://gozasoro.rsvsys.jp/reservations/calendar?date=2026/11/22",
    },
    {
        "date": "11/23",
        "url": "https://gozasoro.rsvsys.jp/reservations/calendar?date=2026/11/23",
    },
]

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
    for target in TARGETS:
        print(f"\n--- {target['date']} の確認 ---")
        try:
            html = fetch(target["url"])
        except Exception as e:
            print(f"取得エラー：{e}")
            continue

        vacancies = extract_vacancy(html)
        print(f"取得した空き状況：{vacancies}")

        if not vacancies:
            print("空き情報が取得できませんでした")
            continue

        for v in vacancies:
            if int(v) >= MIN_VACANCY:
                print(f"{v}名様の空きを検知！メールを送信します。")
                notify(
                    f"【速報】御座候ミュージアム{target['date']}に{v}名様の空きがあります！",
                    f"{target['date']}に{v}名様の空きが出ました！今すぐ予約してください。\n\nhttps://gozasoro.rsvsys.jp/reservations/calendar"
                )
                break
        else:
            print(f"空きなし（現在の状況：{vacancies}）")

if __name__ == "__main__":
    main()
