"""
교보문고 sam 프리미엄 / sam 무제한 일간 베스트 수집
응답이 JSON이 아니라 HTML 조각이라, 정규식으로 순위/제목/저자를 뽑아냅니다.
"""
import json
import os
import re
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

def fetch_html(page_dvsn: str, page: int = 1, per: int = 20):
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
            raw = res.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
    return raw

# 책 한 권 블록에서 순위 / 제목 / 저자·출판사 을 각각 순서대로 추출
RANK_RE = re.compile(r'<em class="rank[^"]*">\s*(\d+)\s*</em>')
TITLE_RE = re.compile(r'<h3>\s*<a[^>]*>([^<]+)</a>\s*</h3>')
INFO_RE = re.compile(r'<p class="prodDt_info">\s*<span>([^<]*)</span>')

def extract_books(html, limit=20):
    ranks = RANK_RE.findall(html)
    titles = TITLE_RE.findall(html)
    authors = INFO_RE.findall(html)

    books = []
    for rank, title, author in zip(ranks, titles, authors):
        books.append({
            "rank": int(rank),
            "title": title.strip(),
            "author": author.strip(),
        })
        if len(books) >= limit:
            break
    return books

def main():
    os.makedirs("data", exist_ok=True)
    for dvsn in ["premium", "unlimited"]:
        print(f"=== sam {dvsn} 요청 시작 ===")
        html = fetch_html(dvsn)
        # 원본도 저장 (파싱 실패 시 구조 재확인용)
        with open(f"data/raw_kyobo_{dvsn}.html", "w", encoding="utf-8") as f:
            f.write(html)
        books = extract_books(html)
        with open(f"data/kyobo_{dvsn}_today.json", "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"[{dvsn}] {len(books)}건 저장 완료")
        for b in books[:5]:
            print(f"  {b['rank']}위 {b['title']} / {b['author']}")

if __name__ == "__main__":
    main()
