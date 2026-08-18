"""
교보문고 sam 프리미엄 / sam 무제한 일간 베스트 수집
1차 목표: 실제 응답이 어떤 모양인지 raw json으로 저장해서 눈으로 확인하는 것.
구조를 확인한 뒤 이 파일의 extract_books() 함수만 다듬으면 됩니다.
"""
import json
import os
import datetime
import urllib.request
import urllib.error

API_URL = "https://sam.kyobobook.co.kr/dig/sam/landing/best/select"

HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://store.kyobobook.co.kr/",
    "Origin": "https://store.kyobobook.co.kr",
    "X-Requested-With": "XMLHttpRequest",
}

def today_str():
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
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            status = res.status
            raw = res.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        # 서버가 4xx/5xx를 줬을 때 — 본문에 이유가 적혀있는 경우가 많음
        status = e.code
        raw = e.read().decode("utf-8", errors="replace")

    print(f"  [{page_dvsn}] HTTP status = {status}")
    print(f"  [{page_dvsn}] 응답 앞부분 500자 미리보기:")
    print("  " + raw[:500].replace("\n", " "))

    if not raw.strip():
        print(f"  [{page_dvsn}] ⚠️ 응답 본문이 비어있습니다.")
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  [{page_dvsn}] ⚠️ JSON이 아닙니다 (HTML 차단 페이지일 가능성).")
        return {"__raw_non_json__": raw}

def extract_books(raw_json):
    if not raw_json or "__raw_non_json__" in raw_json:
        return []
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
        print(f"=== sam {dvsn} 요청 시작 ===")
        raw = fetch(dvsn)
        with open(f"data/raw_kyobo_{dvsn}.json", "w", encoding="utf-8") as f:
            if raw is None:
                json.dump({"error": "empty response"}, f, ensure_ascii=False, indent=2)
            else:
                json.dump(raw, f, ensure_ascii=False, indent=2)
        books = extract_books(raw)
        print(f"[{dvsn}] 추정 도서 {len(books)}건 발견")
        if books:
            print("  첫 항목 샘플:", json.dumps(books[0], ensure_ascii=False)[:300])

if __name__ == "__main__":
    main()
