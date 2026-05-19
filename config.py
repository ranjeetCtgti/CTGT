from __future__ import annotations

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

MIN_CONFIDENCE = 0.3
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

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Query sets
ENGLISH_QUERIES = [
    "Teamcenter administrator",
    "Teamcenter PLM engineer",
    "NX CAD engineer",
    "NX CAM engineer",
    "Solid Edge designer",
    "Polarion ALM engineer",
    "Siemens PLM implementation",
    "Mendix developer Siemens",
    "PLM consultant Teamcenter",
    "Siemens digital industries engineer",
    "Teamcenter integration developer",
    "NX CAD designer manufacturing",
]

GERMAN_QUERIES = [
    "Teamcenter Administrator",
    "NX Konstrukteur",
    "Solid Edge Entwickler",
    "Siemens PLM Berater",
    "PLM Implementierung Teamcenter",
    "Polarion ALM Ingenieur",
]

STEPSTONE_GERMAN_QUERIES = [
    "Teamcenter Administrator",
    "Teamcenter PLM Ingenieur",
    "NX CAD Konstrukteur",
    "NX CAM Programmierer",
    "Solid Edge Konstrukteur",
    "Polarion ALM",
    "Siemens PLM Berater",
    "Mendix Entwickler",
    "PLM Implementierung",
    "Siemens NX Entwickler",
    "CAD Teamcenter Spezialist",
]

LINKEDIN_LOCATIONS = ["Canada", "United States", "United Kingdom"]
INDEED_LOCATIONS = ["Germany", "Canada", "United States"]

GEO_CODE_BY_COUNTRY = {
    "india": "in",
    "germany": "de",
    "canada": "ca",
    "united states": "us",
    "united kingdom": "gb",
}

# Runtime defaults
DEFAULT_BATCH_SIZE = 10
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
