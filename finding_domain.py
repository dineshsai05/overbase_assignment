import pandas as pd
import re
import dns.resolver
from googlesearch import search
from urllib.parse import urlparse
import time

# ---------------- CONFIG ---------------- #

resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8', '8.8.4.4']
resolver.timeout = 5
resolver.lifetime = 5

CORP_KEYWORDS = [
    "inc", "corp", "ltd", "llc", "limited", "company", "co",
    "technologies", "technology", "systems", "solutions",
    "group", "holdings", "networks", "industries"
]

# ---------------- HELPERS ---------------- #

def extract_company(raw):
    """
    Extract the most likely company name from messy lead strings.
    """
    if pd.isna(raw):
        return None

    raw = str(raw).strip()

    # Split on commas
    parts = [p.strip() for p in raw.split(',') if p.strip()]

    # Prefer part with corporate keywords
    for part in reversed(parts):
        if any(k in part.lower() for k in CORP_KEYWORDS):
            return part

    # Otherwise assume last segment is company
    return parts[-1] if parts else raw


def normalize_company(name):
    """
    Normalize company name for search.
    """
    name = name.lower()
    name = re.sub(r'\b(' + '|'.join(CORP_KEYWORDS) + r')\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()


def check_mx(domain):
    """
    Check MX records.
    """
    try:
        answers = resolver.resolve(domain, 'MX')
        return bool(answers)
    except:
        return False


def google_domain(company):
    """
    Search Google and return top domain.
    """
    query = f"{company} official website"
    try:
        for url in search(query, stop=1, pause=2):
            domain = urlparse(url).netloc.lower()
            domain = domain.replace("www.", "")
            return domain
    except:
        return None


# ---------------- CORE LOGIC ---------------- #

def discover_domain(raw_company):
    print(f"🔍 {raw_company}")

    company = extract_company(raw_company)
    if not company or len(company) < 3:
        return "manual_check_required"

    clean = normalize_company(company)

    # --- Step 1: Google search (primary truth source) ---
    domain = google_domain(company)
    if domain:
        if check_mx(domain):
            print(f"✅ Google + MX: {domain}")
            return domain
        else:
            # Google result but MX failed → still keep
            print(f"⚠️ Google only: {domain}")
            return domain

    # --- Step 2: Heuristic fallback ---
    fallback = clean.replace(" ", "") + ".com"
    if check_mx(fallback):
        print(f"✅ Heuristic MX: {fallback}")
        return fallback

   
    print(f"❌ Manual required")
    return "manual_check_required"



df = pd.read_csv("filtered_data.csv")

df["Domain"] = df["Company"].apply(discover_domain)

df = df[df["Domain"] != "manual_check_required"]


df.to_csv("data_with_domains.csv", index=False)
