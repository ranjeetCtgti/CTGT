import csv
from pathlib import Path

from jobspy import scrape_jobs


OUTPUT_CSV = Path("scrape_data.csv")

jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "google"], # "bayt", "naukri", "bdjobs"
    search_term="Software Developer",
    google_search_term="Software Developer",
    location="Germany",
    results_wanted=20,
    hours_old=72,
    country_indeed='Germany',
    
    linkedin_fetch_description=True, # gets more info such as description, direct job url (slower)
    #proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head(40))
jobs.to_csv(
    OUTPUT_CSV,
    mode="a",
    header=not OUTPUT_CSV.exists(),
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    index=False,
)  # append rows for each scrape run
