import pandas as pd
import json
import re

# ------------------ Supported Patterns ------------------

PATTERNS = {
    "first.last": lambda f, l: f"{f}.{l}" if l else None,
    "first": lambda f, l: f"{f}",
    "flast": lambda f, l: f"{f[0]}{l}" if l else None,
    "firstlast": lambda f, l: f"{f}{l}" if l else None,
    "first_last": lambda f, l: f"{f}_{l}" if l else None
}

# ------------------ Name Cleaning ------------------

def clean_name(name):
    if not isinstance(name, str):
        return None, None

    parts = name.lower().strip().split()
    parts = [re.sub(r"[^a-z]", "", p) for p in parts if p]

    if not parts:
        return None, None

    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""

    return first, last

# ------------------ Email Generation ------------------

def generate_two_emails(name, domain, company_patterns):
    if domain not in company_patterns:
        return None

    first, last = clean_name(name)
    if not first:
        return None

    patterns = company_patterns[domain]
    if len(patterns) != 2:
        return None

    emails = []
    for pattern in patterns:
        if pattern not in PATTERNS:
            return None

        local = PATTERNS[pattern](first, last)
        if not local:
            return None

        emails.append(f"{local}@{domain}")

    return emails

# ------------------ Main ------------------

def main():
    df = pd.read_csv("data_with_domains.csv")

    with open("company_patterns.json", "r") as f:
        company_patterns = json.load(f)

    output_rows = []
    MAX_ROWS = 50

    for _, row in df.iterrows():
        if len(output_rows) >= MAX_ROWS:
            break

        name = row.get("Name")
        domain = row.get("Domain")

        emails = generate_two_emails(name, domain, company_patterns)
        if not emails:
            continue

        new_row = row.to_dict()
        new_row["Email_Guess_1"] = emails[0]
        new_row["Email_Guess_2"] = emails[1]

        output_rows.append(new_row)

    out_df = pd.DataFrame(output_rows)
    out_df.to_csv("generated_email_guesses.csv", index=False)

    print(f"Generated exactly {len(out_df)} rows")

if __name__ == "__main__":
    main()
