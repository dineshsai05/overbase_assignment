import pandas as pd
import re

senior_keywords = [
    'Chief', 'CMO', 'CEO', 'CFO', 'COO', 'CTO','CIO','CHRO', 'CAO', 'CSO', 'CISO' , 'CXO', 'VP', 'Vice President', 'Director', 
    'Founder', 'President', 'Head of'
]
pattern = '|'.join(senior_keywords)

df = pd.read_csv('cleaned_data.csv')

df_senior = df[df['Title'].str.contains(pattern, case=False, na=False)].copy()



df_senior.to_csv('filtered_data.csv', index=False)