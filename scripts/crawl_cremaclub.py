"""
크레마클럽(YES24) 인기 순위 수집
이 API는 JSON이 아니라 HTML 조각을 돌려주기 때문에 정규식으로 파싱합니다.
"""
import json
import os
import re
import urllib.request

API_URL = ("https://cremaclub.yes24.com/Bookclub/GetBookclubSumGoodsList"
           "?pageNo=1&pageSize=24&dispNo=&order=10&pageGb=BEST")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://cremaclub.yes24.com/Bookclub/BEST",
}

def fetch_html():
    req = urllib.request.Request(API_URL, headers=HEADERS, method="GET")
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read().decode("utf-8", errors="replace")

# 한 권 블록 예시:
#   <img alt="오뒷세이아" ...>
#   <li class="Num">1</li>
#   <a ...>오뒷세이아</a>
#   <p class="Author">호메로스 저/천병희 역 저</p>
BOOK_BLOCK = re.compile(
    r'"Num">\s*(\d+)\s*<.*?<a[^>]*>\s*([^<]+?)\s*</a>\s*.*?"Author">\s*([^<]+?)\s*<',
    re.DOTALL
)

def extract_books(html, limit=20):
    books = []
    for m in BOOK_BLOCK.finditer(html):
        rank, title, author = m.groups()
        books.append({
            "rank": int(rank),
            "title": title.strip(),
            "author": author.split("/")[0].strip(),  # '저자 저/역자 역' 중 저자만
        })
        if len(books) >= limit:
            break
    return books

def main():
    os.makedirs("data", exist_ok=True)
    html = fetch_html()
    # 원본도 같이 저장 (파싱 실패 시 구조 확인용)
    with open("data/raw_cremaclub.html", "w", encoding="utf-8") as f:
        f.write(html)
    books = extract_books(html)
    with open("data/cremaclub_today.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"크레마클럽 {len(books)}건 저장 완료")
    for b in books[:5]:
        print(f"  {b['rank']}위 {b['title']} / {b['author']}")

if __name__ == "__main__":
    main()
