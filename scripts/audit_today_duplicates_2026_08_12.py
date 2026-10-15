from dotenv import load_dotenv
import os

import psycopg2


load_dotenv(".env")
connection = psycopg2.connect(os.environ["DATABASE_URL"])
cursor = connection.cursor()

queries = {
    "today_companies": """
        SELECT id, company_name, company_domain, signal_count, total_score,
               first_seen, last_updated, contacts
        FROM companies
        WHERE id >= 2196 OR company_domain IN
          ('accuenergy.com','mapleviewenergy.com','horizonaircraft.com','serenitypower.ca')
        ORDER BY company_domain, id
    """,
    "duplicate_domains": """
        SELECT company_domain, COUNT(*), ARRAY_AGG(id ORDER BY id),
               ARRAY_AGG(company_name ORDER BY id)
        FROM companies
        WHERE company_domain IS NOT NULL AND company_domain <> ''
        GROUP BY company_domain HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC, company_domain
    """,
    "today_signals": """
        SELECT id, company_name, company_domain, source_url, detected_at
        FROM signals
        WHERE company_domain IN
          ('accuenergy.com','mapleviewenergy.com','horizonaircraft.com','serenitypower.ca')
        ORDER BY company_domain, id
    """,
    "duplicate_sources": """
        SELECT source_url, COUNT(*), ARRAY_AGG(id ORDER BY id),
               ARRAY_AGG(company_name ORDER BY id)
        FROM signals
        GROUP BY source_url HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC, source_url
    """,
    "today_keyword_links": """
        SELECT kcr.id, kcr.keyword_id, k.keyword, kcr.company_id,
               c.company_name, c.company_domain, kcr.qualification_status,
               kcr.times_seen, kcr.first_discovered_at, kcr.last_seen_at,
               kcr.source_url
        FROM keyword_company_results kcr
        JOIN companies c ON c.id = kcr.company_id
        JOIN keywords k ON k.id = kcr.keyword_id
        WHERE c.company_domain IN
          ('accuenergy.com','mapleviewenergy.com','horizonaircraft.com','serenitypower.ca')
        ORDER BY c.company_domain, kcr.keyword_id
    """,
    "duplicate_keyword_company": """
        SELECT keyword_id, company_id, COUNT(*), ARRAY_AGG(id ORDER BY id)
        FROM keyword_company_results
        GROUP BY keyword_id, company_id HAVING COUNT(*) > 1
    """,
}

for label, query in queries.items():
    print(f"\n## {label}")
    cursor.execute(query)
    for row in cursor.fetchall():
        print(row)

connection.close()
