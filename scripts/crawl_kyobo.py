"""
교보문고 sam 프리미엄 / sam 무제한 일간 베스트 수집
1차 목표: 실제 응답이 어떤 모양인지 raw json으로 저장해서 눈으로 확인하는 것.
구조를 확인한 뒤 이 파일의 extract_books() 함수만 다듬으면 됩니다.
"""
import json
import os
import datetime
import urllib.request

API_URL = "https://sam.kyobobook.co.kr/dig/sam/landing/best/select"

HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://store.kyobobook.co.kr/",
    "Origin": "https://store.kyobobook.co.kr",
}

def today_str():
    # 한국 시간 기준 오늘 날짜 YYYYMMDD
    kst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(kst).strftime("%Y%m%d")

def fetch(page_dvsn: str, page: int = 1, per: int = 20):
    """page_dvsn: 'premium' 또는 'unlimited'"""
    payload = {
        "pageType": "best",
        "lwrnDvsnName": "CMDT_DVSN",
        "page": page,
        "optSrmb": 40,
        "msc": "000",
        "per": str(per),
        "lsc": "EBK",
        "aditYsno": "N",
        "device": "001",
        "pageDvsn": page_dvsn,
        "rdng": "day",
        "rdngVal": today_str(),
        "viewType": "img",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        raw = res.read().decode("utf-8")
    return json.loads(raw)

def extract_books(raw_json):
    """
    ⚠️ raw_kyobo_*.json 을 직접 열어서 실제 구조를 확인한 뒤,
    아래 경로(raw_json["..."]["..."])를 실제 키 이름으로 고쳐주세요.
    지금은 추측으로 몇 가지 흔한 패턴을 시도합니다.
    """
    candidates = []
    if isinstance(raw_json, dict):
        for key in ("data", "result", "resultData", "body"):
            if key in raw_json:
                candidates.append(raw_json[key])
    candidates.append(raw_json)

    for c in candidates:
        if isinstance(c, dict):
            for key in ("list", "items", "bestList", "cmdtList"):
                if key in c and isinstance(c[key], list):
                    return c[key]
        if isinstance(c, list):
            return c
    return []

def main():
    os.makedirs("data", exist_ok=True)
    for dvsn in ["premium", "unlimited"]:
        raw = fetch(dvsn)
        # 1차: 원본 그대로 저장 (구조 확인용)
        with open(f"data/raw_kyobo_{dvsn}.json", "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        books = extract_books(raw)
        print(f"[{dvsn}] 추정 도서 {len(books)}건 발견")
        if books:
            print("  첫 항목 샘플:", json.dumps(books[0], ensure_ascii=False)[:300])

if __name__ == "__main__":
    main()
