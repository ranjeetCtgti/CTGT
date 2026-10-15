from __future__ import annotations

from dotenv import load_dotenv

from db.database import Database


PASSES = [
    ("15:00", {1: 1, 2: 0, 3: 0, 4: 0}),
    ("16:00", {1: 0, 2: 0, 3: 0, 4: 0}),
]


def main() -> None:
    load_dotenv()
    database = Database()
    database.initialize()
    keywords = {keyword.id: keyword for keyword in database.list_keywords()}

    for scheduled_time, results in PASSES:
        print(f"pass={scheduled_time}")
        for keyword_id, result_count in results.items():
            database.record_keyword_search(keyword_id, result_count=result_count)
            print(f"  {keywords[keyword_id].keyword}: published={result_count}")


if __name__ == "__main__":
    main()
