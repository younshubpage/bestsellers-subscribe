"""
밀리의서재 일간 랭킹(종합) 수집
API가 간단한 GET + 인증 불필요라 바로 사용 가능합니다.
"""
import json
import os
import urllib.request

API_URL = ("https://apis.millie.co.kr/public/rank/millie/"
           "?adult=0&size=20&category=total&range=day&book_type_code=01")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.millie.co.kr/",
}

def fetch():
    req = urllib.request.Request(API_URL, headers=HEADERS, method="GET")
    with urllib.request.urlopen(req, timeout=15) as res:
        raw = res.read().decode("utf-8")
    return json.loads(raw)

def extract_books(raw_json, limit=20):
    """확인된 구조: raw_json['data']는 리스트이고, 배열 순서가 곧 순위(1위부터)."""
    items = raw_json.get("data", [])
    books = []
    for i, b in enumerate(items[:limit]):
        books.append({
            "rank": i + 1,
            "title": b.get("book_name", ""),
            "author": (b.get("author") or "").split("/")[0].strip(),  # '지은이 / 옮긴이' 중 지은이만
        })
    return books

def main():
    os.makedirs("data", exist_ok=True)
    raw = fetch()
    books = extract_books(raw)
    with open("data/millie_today.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"밀리의서재 {len(books)}건 저장 완료")
    for b in books[:5]:
        print(f"  {b['rank']}위 {b['title']} / {b['author']}")

if __name__ == "__main__":
    main()
