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

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"[WARN] 리스트 형식이 아님: {path}")
            return []

        return data

    except Exception as e:
        print(f"[ERROR] JSON 읽기 실패: {path}")
        print(e)
        return []


def load_store(path):
    raw = load_json(path)

    result = []

    for item in raw:
        title = item.get("title", "")
        author = item.get("author", "")
        rank = item.get("rank")

        if not title or rank is None:
            continue

        try:
            rank = int(rank)
        except:
            continue

        # 각 사이트별 1~20위만 사용
        if rank < 1 or rank > 20:
            continue

        result.append({
            "rank": rank,
            "title": title,
            "author": author
        })

    # 순위순 정렬
    result.sort(key=lambda x: x["rank"])

    return result[:20]


def build():

    data = {}

    for store_key, path in SOURCES.items():

        books = load_store(path)

        data[store_key] = books

        print(f"{store_key}: {len(books)}권")

    today = datetime.now().strftime("%Y-%m-%d")
    prev = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    result = {
        "today": today,
        "prev": prev,

        "categories": [
            {
                "id": "comparison",
                "label": "사이트별 TOP 20"
            }
        ],

        "data": {
            "comparison": data
        }
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("")
    print("[OK] data.json 생성 완료")
    print(f"[OK] 날짜: {today}")

    for key, books in data.items():
        print(f"[OK] {key}: {len(books)}권")


if __name__ == "__main__":
    build()
