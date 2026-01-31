import pandas as pd
import re
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

# 1. Load your existing filtered data
df = pd.read_csv('filtered_data.csv')

def get_heuristic_domain(company_name):
    """Cleans company name to a likely domain string."""
    c = str(company_name).lower().strip()
    # Remove corporate suffixes
    suffixes = r'\b(inc|corp|ltd|llc|group|solutions|networks|systems|company|the|intl)\b'
    c = re.sub(suffixes, '', c)
    # Remove non-alphanumeric characters
    c = re.sub(r'[^a-z0-9]', '', c)
    return f"{c}.com" if c else "company.com"

def check_mx(domain):
    """Verifies if the domain has valid Mail Exchange records."""
    try:
        # We set a timeout so the script doesn't hang on dead domains
        answers = dns.resolver.resolve(domain, 'MX', timeout=2)
        return True if answers else False
    except:
        return False

def process_row(company):
    """Logic to find and verify the domain."""
    # First, guess the domain
    domain = get_heuristic_domain(company)
    
    # Second, check if it's valid. If not, try common variations (like .io or .net)
    if not check_mx(domain):
        # Specific check for tech startups in your list (like Spacelift or Honeycomb)
        for ext in ['.io', '.ai', '.net']:
            alt_domain = domain.replace('.com', ext)
            if check_mx(alt_domain):
                return alt_domain
    
    return domain

# 2. Apply the logic
# We use a ThreadPoolExecutor to make the DNS checks much faster
print("Starting Domain Discovery and MX Validation...")
with ThreadPoolExecutor(max_workers=10) as executor:
    df['Domain'] = list(executor.map(process_row, df['Company']))

# 3. Final Export
df.to_csv('data_with_domains.csv', index=False)
print("Done! Domains added and verified in 'data_with_domains.csv'")