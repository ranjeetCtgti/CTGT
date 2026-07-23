from __future__ import annotations

import os
from pathlib import Path

# Supported software names used throughout extraction/scoring.
SOFTWARE_CANONICAL = {
    "teamcenter",
    "nx",
    "solid edge",
    "polarion",
    "mendix",
    "opcenter",
    "xcelerator",
}

ALLOWED_SOFTWARE_NAMES = {
    "Teamcenter",
    "NX",
    "Solid Edge",
    "Polarion",
    "Mendix",
    "Opcenter",
    "Xcelerator",
    "Siemens PLM",
}

SOFTWARE_DISPLAY_TO_CANONICAL = {
    "Teamcenter": "teamcenter",
    "NX": "nx",
    "Solid Edge": "solid edge",
    "Polarion": "polarion",
    "Mendix": "mendix",
    "Opcenter": "opcenter",
    "Xcelerator": "xcelerator",
    "Siemens PLM": "xcelerator",
}

SOFTWARE_CANONICAL_TO_DISPLAY = {
    "teamcenter": "Teamcenter",
    "nx": "NX",
    "solid edge": "Solid Edge",
    "polarion": "Polarion",
    "mendix": "Mendix",
    "opcenter": "Opcenter",
    "xcelerator": "Xcelerator",
}

SOFTWARE_ALIASES = {
    "teamcenter": {"teamcenter", "tc", "siemens teamcenter", "team center"},
    "nx": {"nx", "nx cad", "nx cam", "siemens nx", "ug nx", "unigraphics"},
    "solid edge": {"solid edge", "solidedge", "siemens solid edge"},
    "polarion": {"polarion", "polarion alm", "siemens polarion"},
    "mendix": {"mendix", "siemens mendix", "low code mendix"},
    "opcenter": {"opcenter", "siemens opcenter", "simatic it", "mes opcenter"},
    "xcelerator": {"xcelerator", "siemens xcelerator"},
}

PLM_KEYWORDS = {
    "Teamcenter": [
        "teamcenter",
        "teamcenter x",
        "teamcenter manufacturing",
        "teamcenter mes",
        "teamcenter rapid author",
        "tc plm",
        "tc administration",
        "siemens teamcenter",
        "teamcenter integration",
        "teamcenter upgrade",
        "teamcenter migration",
        "product lifecycle management siemens",
    ],
    "NX": [
        "siemens nx",
        "nx cad",
        "nx cam",
        "nx cae",
        "nx nastran",
        "nx designer",
        "nx engineer",
        "nx modeling",
        "nx manufacturing",
        "unigraphics",
        "ugii",
    ],
    "Solid Edge": [
        "solid edge",
        "solid edge cad",
        "solid edge designer",
        "solid edge simulation",
        "solid edge manufacturing",
        "solid edge for manufacturing",
    ],
    "Polarion": [
        "polarion",
        "polarion alm",
        "polarion requirements",
        "siemens polarion",
        "polarion testng",
    ],
    "Mendix": [
        "mendix",
        "mendix developer",
        "mendix low-code",
        "mendix platform",
        "siemens mendix",
    ],
    "Siemens_General": [
        "siemens plm",
        "siemens digital industries",
        "siemens opcenter",
        "siemens mindsphere",
        "xcelerator",
        "siemens eda",
        "capital electra",
    ],
}

PLM_KEYWORDS_DE = {
    "Teamcenter": ["teamcenter", "tc-administration", "plm siemens"],
    "NX": ["siemens nx", "nx konstrukteur", "nx entwickler", "unigraphics"],
    "Solid Edge": ["solid edge", "solid edge konstrukteur"],
    "Polarion": ["polarion", "polarion alm"],
    "Mendix": ["mendix entwickler", "mendix plattform"],
}

MIGRATION_SIGNAL_PHRASES = [
    "migrating from windchill",
    "replacing windchill",
    "transition from enovia",
    "moving from catia",
    "ptc windchill",
    "dassault systemes",
    "enovia",
    "autodesk vault",
    "autodesk pdm",
    "sap plm",
    "legacy pdm",
    "legacy plm system",
    "replace our current plm",
    "evaluating plm solutions",
]

PAIN_SIGNAL_PHRASES = [
    "implementation",
    "rollout",
    "go-live",
    "integration",
    "deployment",
    "migration",
    "migration project",
    "upgrade",
    "support engineer",
    "system administrator",
    "customization",
    "integration developer",
    "consultant",
    "managed services",
    "post go-live",
    "change management",
]

EXPANSION_SIGNAL_PHRASES = [
    "scaling engineering team",
    "new r&d center",
    "new manufacturing facility",
    "new plant",
    "digital transformation",
    "industry 4.0",
    "smart manufacturing",
    "growing team",
    "expanding operations",
]

EXCLUDED_COMPANIES = [
    "siemens ag",
    "siemens",
    "ptc inc",
    "dassault systemes",
    "autodesk",
    "ansys",
    "hexagon ab",
    "aveva",
    "opentext",
    "w3global",
    "sri tech solutions inc",
    "sri tech solutions inc.",
]

# Structured scraper metadata and extraction results use this list to remove
# service-sector employers before persistence. Keep these values lowercase;
# matching is case-insensitive and covers more specific labels such as
# "IT Services and IT Consulting".
EXCLUDED_INDUSTRIES = [
    # 1. IT & Software Services
    "it services",
    "it consulting",
    "information technology",
    "information services",
    "software development",
    "computer software",
    "enterprise software",
    "saas",
    "cloud services",
    "technology, information and media",
    "information and media",
    "internet publishing",
    "internet marketplace platforms",

    # 2. Consulting & Advisory
    "consulting",
    "management consulting",
    "business consulting",
    "technology consulting",
    "plm consulting",
    "plm services",
    "advisory",
    "professional services",
    "system integrator",
    "integrator",
    "hospitality",
    "retail",
    "health and human services",
    "hospitals and health care",
    "hospital & health care",
    "medical practice",
    "health, wellness & fitness",
    "banking",
    "financial services",
    "investment management",
    "insurance",
    "consumer services",
    "government administration",
    "civic and social organizations",
    "technology, information and internet",

    # 3. Staffing, Recruiting & Talent
    "staffing",
    "recruiting",
    "talent solutions",
    "human resources",
    "human resources services",
    "employment agency",
    "outsourcing",
    "bpo",

    # 4. Agencies & Digital Transformation
    "agency",
    "digital agency",
    "marketing services",
    "market research",
    "public relations & communications",
    "technical consulting",
    "non-profit organizations",
    "non-profit organizations and primary and secondary education",
    "education",
    "professional training & coaching",
    "construction",
    "civil engineering",
    "logistics & supply chain",
    "sports",
    "music",
]

# Canonical labels the extraction model can use when a scraper does not provide
# structured industry metadata (notably Stepstone and news feeds).
EXCLUDED_INDUSTRY_CATEGORIES = [
    "IT & Software Services",
    "Consulting & Advisory",
    "Staffing, Recruiting & Outsourcing",
    "Hospitality",
    "Retail",
    "Healthcare & Human Services",
    "Banking & Financial Services",
    "Insurance",
    "Consumer Services",
    "Government & Civic Organizations",
    "Nonprofit & Education",
]

# Scoring
SIGNAL_TYPE_BASE_SCORE = {
    "job_posting": 10,
    "career_page": 25,
    "news": 20,
}

SOURCE_BASE_SCORE = {
    "linkedin": 10,
    "indeed": 10,
    "google": 10,
    "stepstone": 10,
    "career_page": 25,
    "news": 20,
}

SOFTWARE_SCORE = {
    "teamcenter": 30,
    "nx": 25,
    "solid edge": 22,
    "polarion": 18,
    "mendix": 18,
    "opcenter": 16,
    "xcelerator": 15,
}

MIGRATION_BONUS = 25
PAIN_SIGNAL_BONUS_PER_MATCH = 10
PAIN_SIGNAL_BONUS_MAX = 30
EXPANSION_SIGNAL_BONUS_PER_MATCH = 15
EXPANSION_SIGNAL_BONUS_MAX = 30

VOLUME_BONUS_SECOND_SIGNAL = 15
VOLUME_BONUS_THIRD_PLUS_SIGNAL = 20
MULTI_SOURCE_BONUS = 25

LEAD_THRESHOLDS = {
    "hot": 70,
    "warm": 35,
}

MIN_CONFIDENCE = 0.65
MIN_RELEVANT_CONTEXT_CHARS = 50

INDUSTRY_CHOICES = [
    "Automotive",
    "Aerospace",
    "Industrial Equipment",
    "Electronics",
    "Medical Devices",
    "Energy",
    "Rail",
    "Other Manufacturing",
    "Unknown",
]

MODEL_INDUSTRY_CHOICES = INDUSTRY_CHOICES + EXCLUDED_INDUSTRY_CATEGORIES

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Query sets
ENGLISH_QUERIES = [
    "Teamcenter administrator",
    "Teamcenter PLM engineer",
    "Teamcenter migration engineer",
    "Teamcenter support engineer",
    "Teamcenter solution architect",
    "NX CAD engineer",
    "NX CAM engineer",
    "NX CAD designer manufacturing",
    # "Solid Edge designer",
    "Polarion ALM engineer",
    "Polarion requirements engineer",
    "Polarion test manager",
    "Polarion consultant",
    # "Siemens PLM implementation",
    "Mendix developer Siemens",
    "Mendix low-code developer",
    "Mendix application architect",
    "Mendix manufacturing consultant",
    "Mendix platform engineer",
    "Mendix solution architect",
    "PLM consultant Teamcenter",
    # "Siemens digital industries engineer",
    "Teamcenter integration developer",
]

GERMAN_QUERIES = [
    "Teamcenter Administrator",
    "PLM Implementierung Teamcenter",
    "Teamcenter Migration Ingenieur",
    "Polarion ALM Ingenieur",
    "Polarion Berater",
    "Polarion Requirements Engineer",
    "Mendix Entwickler",
    "Mendix Low-Code Entwickler",
    "Mendix Berater",
    "Mendix Plattform Entwickler",
    "Mendix Solution Architekt",
    "NX Konstrukteur",
    "NX Entwickler",
    # "Solid Edge Entwickler",
    # "Siemens PLM Berater",
]

STEPSTONE_GERMAN_QUERIES = [
    "Teamcenter Administrator",
    "Teamcenter PLM Ingenieur",
    "Teamcenter Migration Ingenieur",
    "Teamcenter Support Ingenieur",
    "NX CAD Konstrukteur",
    "NX CAM Programmierer",
    "Siemens NX Entwickler",
    # "Solid Edge Konstrukteur",
    "Polarion ALM",
    "Polarion Berater",
    "Polarion Requirements Engineer",
    # "Siemens PLM Berater",
    "Mendix Entwickler",
    "Mendix Low-Code Entwickler",
    "Mendix Berater",
    # "PLM Implementierung",
    "CAD Teamcenter Spezialist",
]

LINKEDIN_LOCATIONS = ["Canada", "Germany", "United States"]
INDEED_LOCATIONS = ["Canada", "Germany", "United States"]
GOOGLE_LOCATIONS = ["Canada", "Germany", "United States"]

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CAREER_PAGE_TARGETS_CSV = DATA_DIR / "career_page_targets.csv"

CAREER_PAGE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
]
CAREER_PAGE_MAX_PAGES_PER_TARGET = 4

NEWS_RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Teamcenter+implementation&hl=en",
    "https://news.google.com/rss/search?q=Teamcenter+digital+transformation&hl=en",
    "https://news.google.com/rss/search?q=Teamcenter+migration&hl=en",
    "https://news.google.com/rss/search?q=Teamcenter+upgrade&hl=en",
    "https://news.google.com/rss/search?q=Polarion+ALM+deployment&hl=en",
    "https://news.google.com/rss/search?q=Polarion+requirements+management&hl=en",
    "https://news.google.com/rss/search?q=Polarion+implementation&hl=en",
    "https://news.google.com/rss/search?q=Mendix+digital+transformation&hl=en",
    "https://news.google.com/rss/search?q=Mendix+low-code+platform&hl=en",
    "https://news.google.com/rss/search?q=Mendix+manufacturing&hl=en",
    "https://news.google.com/rss/search?q=NX+CAD+Siemens+company&hl=en",
    "https://news.google.com/rss/search?q=NX+manufacturing+Siemens&hl=en",
    # "https://news.google.com/rss/search?q=Siemens+PLM+rollout&hl=en",
    # 'https://news.google.com/rss/search?q="Solid+Edge"+manufacturing&hl=en',
    # "https://news.google.com/rss/search?q=Siemens+Xcelerator+implementation&hl=en",
    "https://news.google.com/rss/search?q=Teamcenter+Implementierung&hl=de",
    "https://news.google.com/rss/search?q=NX+Siemens+Implementierung&hl=de",
    "https://news.google.com/rss/search?q=Polarion+ALM+Einfuhrung&hl=de",
    "https://news.google.com/rss/search?q=Mendix+Implementierung&hl=de",
    # "https://news.google.com/rss/search?q=Siemens+PLM+Einfuhrung&hl=de",
]
NEWS_RSS_USER_AGENT = "CTGT-NewsBot/1.0"

GEO_CODE_BY_COUNTRY = {
    "australia": "au",
    "france": "fr",
    "germany": "de",
    "canada": "ca",
    "united states": "us",
    "united kingdom": "gb",
}

# Runtime defaults
DEFAULT_BATCH_SIZE = 5
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
CAREER_PAGE_MAX_TEXT_CHARS = 12000
NEWS_RSS_DESCRIPTION_MAX_CHARS = 4000

DEFAULT_ENRICHMENT_TIMEOUT_SECONDS = 10
DEFAULT_ENRICHMENT_MIN_DOMAIN_CONFIDENCE = 0.74
DEFAULT_LEAD_ENRICHMENT_TIMEOUT_SECONDS = 10
DEFAULT_LEAD_ENRICHMENT_FRESHNESS_DAYS = 7
