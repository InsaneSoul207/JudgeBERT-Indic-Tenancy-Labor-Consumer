"""
Test fetcher script for authentic legislative text.
"""
import urllib.request
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def fetch_prs_bill(url):
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract all text blocks from main content
    text_blocks = []
    for tag in soup.find_all(['p', 'li']):
        txt = tag.get_text().strip()
        # Clean whitespace
        txt = re.sub(r'\s+', ' ', txt)
        if len(txt) > 50 and not any(skip in txt.lower() for skip in ['sign up', 'fellowship', 'cookie', 'javascript', 'lamp fellowship']):
            text_blocks.append(txt)
            
    print(f"Extracted {len(text_blocks)} authentic blocks from {url}")
    return text_blocks

if __name__ == "__main__":
    cpa_blocks = fetch_prs_bill("https://prsindia.org/billtrack/the-consumer-protection-bill-2019")
    mta_blocks = fetch_prs_bill("https://prsindia.org/billtrack/the-model-tenancy-act-2021")
    
    print("\nSample Consumer Protection Clauses:")
    for b in cpa_blocks[:4]:
        print(">>", b[:140])
        
    print("\nSample Model Tenancy Act Clauses:")
    for b in mta_blocks[:4]:
        print(">>", b[:140])
