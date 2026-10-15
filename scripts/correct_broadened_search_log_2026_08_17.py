from dotenv import load_dotenv
from sqlalchemy import text

from db.database import Database


FINAL_COUNTS = {1: 0, 2: 1, 3: 1, 4: 0, 5: 4, 7: 6, 8: 9, 9: 14, 10: 6, 11: 0, 12: 1, 13: 5}


load_dotenv(".env")
database = Database()
database.initialize()
with database.engine.begin() as connection:
    # The broadened worker was accidentally launched twice in parallel. Its
    # idempotent persistence kept evidence correct, but each launch incremented
    # the search counter. Remove the duplicate increment and retain the final
    # qualified + watchlist count after exact-keyword rehoming.
    for keyword_id, result_count in FINAL_COUNTS.items():
        connection.execute(
            text(
                """
                UPDATE keywords
                SET search_count = GREATEST(search_count - 1, 0),
                    last_result_count = :result_count,
                    last_error = NULL
                WHERE id = :keyword_id
                """
            ),
            {"keyword_id": keyword_id, "result_count": result_count},
        )
