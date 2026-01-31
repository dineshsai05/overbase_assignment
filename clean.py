import pandas as pd
import re

processed_data = []

#merging 2nd and 3rd columns if the row has 5 entries
with open('cmo_videos_names.csv', 'r') as f:
    lines = f.readlines()
    for line in lines[1:]: 
        parts = [p.strip() for p in line.split(',')]
        if len(parts) == 5:
            # Merge 2nd and 3rd columns
            name, title, company, url = parts[0], f"{parts[1]} {parts[2]}", parts[3], parts[4]
        elif len(parts) == 4:
            name, title, company, url = parts[0], parts[1], parts[2], parts[3]
        else:
            continue 
            
        processed_data.append({'Name': name, 'Title': title, 'Company': company})

df = pd.DataFrame(processed_data)

#remove row if any column is empty
df.dropna()

def is_valid(val):
    # Convert to string and search for any alphanumeric character
    return bool(re.search(r'[a-zA-Z0-9]', str(val)))

df_cleaned = df[df.apply(lambda row: row.map(is_valid).all(), axis=1)].copy()

trash_phrases = [
    r'\(Title not stated\)', 
    r'\(Title not specified\)', 
    r'\(Company not stated\)'
]
pattern = '|'.join(trash_phrases)

# 2. Use '&' to ensure BOTH Title and Company are clean
# 3. Use 'df_cleaned' consistently if you are overwriting it
df_cleaned = df_cleaned[
    ~df_cleaned['Title'].str.strip().str.contains(pattern, case=False, na=False) & 
    ~df_cleaned['Company'].str.strip().str.contains(pattern, case=False, na=False)
].copy()

df_cleaned.to_csv('cleaned_data.csv', index=False)