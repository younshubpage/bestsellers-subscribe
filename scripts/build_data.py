import json
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT = ROOT / "data.json"

SOURCES = {
    "cremaclub": DATA_DIR / "cremaclub_today.json",
    "millie": DATA_DIR / "millie_today.json",
    "sam_premium": DATA_DIR / "kyobo_premium_today.json",
    "sam_unlimited": DATA_DIR / "kyobo_unlimited_today.json",
}


def load_json(path):
    if not path.exists():
        print(f"[WARN] 파일 없음: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_book_key(title, author):
    """
    제목과 저자를 원본 그대로 사용해서 책을 식별한다.

    중요:
    - 띄어쓰기 차이 → 다른 책
    - 괄호 차이 → 다른 책
    - 오탈자 → 다른 책
    - 지음/저 등의 표기 차이 → 다른 책
    - 저자명 차이 → 다른 책

    즉, title과 author가 모두 완전히 동일한 경우에만
    같은 책으로 인식한다.
    """
    return f"{title}|{author}"


def load_store(store_key, path):
    raw = load_json(path)

    result = []

    for item in raw:
        title = item.get("title", "")
        author = item.get("author", "")
        rank = item.get("rank")

        if not title or rank is None:
            continue

        result.append({
            "rank": int(rank),
            "title": title,
            "author": author,
        })

    return result


def build():
    stores = {}

    # 각 서비스 데이터 불러오기
    for key, path in SOURCES.items():
        stores[key] = load_store(key, path)
        print(f"{key}: {len(stores[key])}권")

    # 책들을 하나로 합침
    books = {}

    for store_key, items in stores.items():
        for item in items:

            # ★ 제목 + 저자 원본값 그대로 비교
            key = make_book_key(
                item["title"],
                item["author"]
            )

            if key not in books:
                books[key] = {
                    "isbn": key,
                    "title": item["title"],
                    "author": item["author"],
                    "pub": "",
                }

            books[key][store_key] = {
                "t": item["rank"],
                "p": None,
            }

    # 현재 순위 기준으로 전체 책 정렬
    book_list = list(books.values())

    book_list.sort(
        key=lambda b: min(
            [
                b[s]["t"]
                for s in SOURCES
                if s in b
            ]
        )
    )

    # 최대 20권
    book_list = book_list[:20]

    # 데이터 구조
    data = {
        "all": {
            "books": book_list
        }
    }

    # 현재 날짜
    today = datetime.now().strftime("%Y-%m-%d")

    result = {
        "today": today,
        "prev": (
            datetime.now() - timedelta(days=1)
        ).strftime("%Y-%m-%d"),
        "surge_gap": 4,

        "categories": [
            {
                "id": "all",
                "label": "전체"
            }
        ],

        "data": data
    }

    # data.json 저장
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("[OK] data.json 생성 완료")
    print(f"[OK] 책 수: {len(book_list)}")
    print(f"[OK] 날짜: {today}")


if __name__ == "__main__":
    build()
