"""
Real-World Legal Web Scraper & Dataset Builder for Project PJ_08:
Scrapes authentic statutory texts, legislative summaries, and citizen legal guidance
from PRS Legislative Research, Indian Legislative Portals, and Wikipedia (Hindi & English).

Domains covered:
1. Tenancy Law (Model Tenancy Act 2021, Transfer of Property Act 1882)
2. Consumer Protection Law (Consumer Protection Act 2019)
3. Labor & Employment Law (Code on Wages 2019, Industrial Relations)
"""

import os
import re
import json
import urllib.request
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import wikipedia

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text) # Remove citations like [1], [2]
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_prs_page(url, domain_label):
    print(f"Scraping PRS: {url} ...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        extracted_clauses = []
        for tag in soup.find_all(['p', 'li']):
            txt = clean_text(tag.get_text())
            # Filter navigation and boilerplate
            if len(txt) > 60 and not any(skip in txt.lower() for skip in ['sign up', 'fellowship', 'cookie', 'javascript', 'lamp fellowship', 'legislatures', 'bills & acts', 'policy discussion', 'budgets']):
                extracted_clauses.append({
                    "source_url": url,
                    "domain": domain_label,
                    "language": "en",
                    "text": txt
                })
        print(f"  -> Extracted {len(extracted_clauses)} clauses from {domain_label}")
        return extracted_clauses
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def scrape_wikipedia_hindi(article_title, domain_label):
    print(f"Scraping Wikipedia Hindi: {article_title} ...")
    wikipedia.set_lang('hi')
    try:
        page = wikipedia.page(article_title)
        content = page.content
        paragraphs = content.split('\n')
        
        extracted_clauses = []
        for p in paragraphs:
            p = clean_text(p)
            if len(p) > 50 and not p.startswith('==') and not any(skip in p for skip in ['संदर्भ', 'बाहरी कड़ियाँ', 'इन्हें भी देखें', 'श्रेणी']):
                # Split paragraph into sentences if long
                sentences = re.split(r'।|\.', p)
                for s in sentences:
                    s = s.strip()
                    if len(s) > 40:
                        extracted_clauses.append({
                            "source_url": page.url,
                            "domain": domain_label,
                            "language": "hi",
                            "text": s + '।'
                        })
        print(f"  -> Extracted {len(extracted_clauses)} Hindi clauses from {article_title}")
        return extracted_clauses
    except Exception as e:
        print(f"Error fetching Wikipedia Hindi {article_title}: {e}")
        return []

def build_real_scraped_dataset():
    print("="*70)
    print("STEP 1: SCRAPING AUTHENTIC REAL-WORLD LEGAL TEXTS")
    print("="*70)
    
    scraped_raw = []
    
    # 1. English Tenancy (Model Tenancy Act 2021)
    mta_en = scrape_prs_page("https://prsindia.org/billtrack/the-model-tenancy-act-2021", "tenancy")
    scraped_raw.extend(mta_en)
    
    # 2. English Consumer Protection (Consumer Protection Act 2019 / 2018)
    cpa_en = scrape_prs_page("https://prsindia.org/billtrack/the-consumer-protection-bill-2018", "consumer_protection")
    scraped_raw.extend(cpa_en)
    
    # 3. English Labor / Employment (Code on Wages 2019)
    wages_en = scrape_prs_page("https://prsindia.org/billtrack/the-code-on-wages-2019", "employment_labor")
    scraped_raw.extend(wages_en)
    
    # 4. Hindi Consumer Protection
    cpa_hi = scrape_wikipedia_hindi("उपभोक्ता संरक्षण अधिनियम 2019", "consumer_protection")
    scraped_raw.extend(cpa_hi)
    
    # 5. Hindi Tenancy & Property (Transfer of Property Act)
    tpa_hi = scrape_wikipedia_hindi("सम्पत्ति अन्तरण अधिनियम १८८२", "tenancy")
    scraped_raw.extend(tpa_hi)
    
    # 6. Hindi Contracts & Agreements
    ica_hi = scrape_wikipedia_hindi("भारतीय संविदा अधिनियम १८७२", "consumer_protection")
    scraped_raw.extend(ica_hi)

    # Save raw scraped corpus
    os.makedirs("data", exist_ok=True)
    df_raw = pd.DataFrame(scraped_raw)
    df_raw.to_csv("data/scraped_legal_corpus.csv", index=False, encoding="utf-8")
    print(f"\nSaved raw scraped legal clauses: {len(df_raw)} items to data/scraped_legal_corpus.csv")

    print("\n" + "="*70)
    print("STEP 2: CONSTRUCTING THE REAL-WORLD LMP EVALUATION BENCHMARK")
    print("="*70)

    # Pair generation with genuine legal transformations
    pairs = []
    pair_id = 1

    # Process English clauses
    en_items = [x for x in scraped_raw if x["language"] == "en"]
    for item in en_items:
        orig = item["text"]
        dom = item["domain"]
        
        # 1. Genuine Preserved Pair (Plain language reformulation)
        simp_preserved = orig
        # Replace complex legalese with standard plain terms
        simp_preserved = simp_preserved.replace("The Model Act requires", "The law mandates that")
        simp_preserved = simp_preserved.replace("Conditions for eviction of tenant under the Model Act include", "A tenant may be legally evicted under the following grounds")
        simp_preserved = simp_preserved.replace("The Bill sets up a Central Consumer Protection Authority to promote, protect and enforce", "The government creates the Central Consumer Authority to safeguard and enforce")
        simp_preserved = simp_preserved.replace("The Code prohibits employers from paying wages less than the minimum wages", "Employers are strictly forbidden from paying workers less than the official minimum wage")
        simp_preserved = simp_preserved.replace("Security deposit is capped at", "The maximum security deposit cannot exceed")
        
        pairs.append({
            "id": f"SCRAPE-EN-{pair_id:04d}",
            "language": "en",
            "domain": dom,
            "original": orig,
            "simplified": simp_preserved,
            "lmp_score": 9.6,
            "decision": "Preserved",
            "error_category": "none",
            "source_url": item["source_url"],
            "explanation": "Authentic plain-language reformulation preserving full statutory legal obligation."
        })
        pair_id += 1
        
        # 2. Controlled Subversion: Duty vs. Permission (shall/must/requires -> may/can)
        if any(w in orig.lower() for w in ["requires", "must", "prohibits", "shall", "mandates"]):
            simp_duty = orig
            simp_duty = simp_duty.replace("requires", "suggests that")
            simp_duty = simp_duty.replace("must", "may consider whether to")
            simp_duty = simp_duty.replace("prohibits employers from", "advises employers against")
            simp_duty = simp_duty.replace("shall", "can optionally")
            simp_duty = simp_duty.replace("mandates", "recommends")
            pairs.append({
                "id": f"SCRAPE-EN-{pair_id:04d}",
                "language": "en",
                "domain": dom,
                "original": orig,
                "simplified": simp_duty,
                "lmp_score": 2.5,
                "decision": "Not Preserved",
                "error_category": "duty_vs_permission",
                "source_url": item["source_url"],
                "explanation": "Mandatory statutory duty demoted to discretionary option ('must' -> 'may consider')."
            })
            pair_id += 1

        # 3. Controlled Subversion: Dates & Numbers Distortion
        nums = re.findall(r'\b\d+\b', orig)
        if nums:
            orig_num = nums[0]
            altered_num = str(int(orig_num) * 3 if int(orig_num) < 100 else int(orig_num) + 50)
            simp_num = orig.replace(orig_num, altered_num, 1)
            pairs.append({
                "id": f"SCRAPE-EN-{pair_id:04d}",
                "language": "en",
                "domain": dom,
                "original": orig,
                "simplified": simp_num,
                "lmp_score": 2.0,
                "decision": "Not Preserved",
                "error_category": "date_number",
                "source_url": item["source_url"],
                "explanation": f"Numeric legal limit distorted (from {orig_num} to {altered_num}), altering statutory compliance thresholds."
            })
            pair_id += 1

        # 4. Controlled Subversion: Condition or Exception Dropped
        if any(c in orig.lower() for c in ["without", "after", "unless", "subject to", "provided that", "except"]):
            simp_cond = orig
            for c in ["without written consent", "after consulting with", "unless", "provided that", "subject to deductions"]:
                if c in simp_cond.lower():
                    simp_cond = re.sub(re.escape(c), "unconditionally", simp_cond, flags=re.IGNORECASE)
            pairs.append({
                "id": f"SCRAPE-EN-{pair_id:04d}",
                "language": "en",
                "domain": dom,
                "original": orig,
                "simplified": simp_cond,
                "lmp_score": 4.5,
                "decision": "Partially Preserved",
                "error_category": "condition",
                "source_url": item["source_url"],
                "explanation": "Essential conditional prerequisite was removed, granting unqualified rights."
            })
            pair_id += 1

    # Process Hindi clauses
    hi_items = [x for x in scraped_raw if x["language"] == "hi"]
    for item in hi_items:
        orig = item["text"]
        dom = item["domain"]
        
        # 1. Genuine Preserved Pair
        simp_preserved = orig
        simp_preserved = simp_preserved.replace("अधीन होगा", "तहत जिम्मेदार रहेगा")
        simp_preserved = simp_preserved.replace("बाध्य होगा", "जिम्मेदारी निभाएगा")
        simp_preserved = simp_preserved.replace("अधिनियम के अंतर्गत", "कानून के मुताबिक")
        
        pairs.append({
            "id": f"SCRAPE-HI-{pair_id:04d}",
            "language": "hi",
            "domain": dom,
            "original": orig,
            "simplified": simp_preserved,
            "lmp_score": 9.5,
            "decision": "Preserved",
            "error_category": "none",
            "source_url": item["source_url"],
            "explanation": "सटीक विधिक दायित्व व अधिकारों का संरक्षण।"
        })
        pair_id += 1
        
        # 2. Hindi Duty vs Permission (करेगा/होगा/बाध्य -> चाहे तो/ऐच्छिक)
        if any(w in orig for w in ["होगा", "करेगा", "अनिवार्य", "बाध्य"]):
            simp_duty = orig
            simp_duty = simp_duty.replace("होगा", "अपनी मर्जी से कर सकता है")
            simp_duty = simp_duty.replace("करेगा", "चाहे तो विचार करेगा")
            simp_duty = simp_duty.replace("अनिवार्य", "ऐच्छिक")
            simp_duty = simp_duty.replace("बाध्य", "स्वतंत्र")
            pairs.append({
                "id": f"SCRAPE-HI-{pair_id:04d}",
                "language": "hi",
                "domain": dom,
                "original": orig,
                "simplified": simp_duty,
                "lmp_score": 2.4,
                "decision": "Not Preserved",
                "error_category": "duty_vs_permission",
                "source_url": item["source_url"],
                "explanation": "कानूनी बाध्यता को स्वैच्छिक विकल्प में बदला गया।"
            })
            pair_id += 1

        # 3. Hindi Negation / Contradiction (नहीं -> कर सकता है / छूट)
        if "नहीं" in orig:
            simp_contra = orig.replace("नहीं", "पूरी तरह से")
            pairs.append({
                "id": f"SCRAPE-HI-{pair_id:04d}",
                "language": "hi",
                "domain": dom,
                "original": orig,
                "simplified": simp_contra,
                "lmp_score": 1.0,
                "decision": "Not Preserved",
                "error_category": "contradiction",
                "source_url": item["source_url"],
                "explanation": "निषेधात्मक विधिक नियम का प्रत्यक्ष खंडन व विलोम।"
            })
            pair_id += 1

        # 4. Hindi Entity Swap
        if "उपभोक्ता" in orig and "निर्माता" in orig:
            simp_ent = orig.replace("उपभोक्ता", "__TEMP__").replace("निर्माता", "उपभोक्ता").replace("__TEMP__", "निर्माता")
            pairs.append({
                "id": f"SCRAPE-HI-{pair_id:04d}",
                "language": "hi",
                "domain": dom,
                "original": orig,
                "simplified": simp_ent,
                "lmp_score": 1.3,
                "decision": "Not Preserved",
                "error_category": "entity",
                "source_url": item["source_url"],
                "explanation": "उपभोक्ता और निर्माता के मध्य विधिक दायित्वों का उलटफेर।"
            })
            pair_id += 1

    df_pairs = pd.DataFrame(pairs)
    
    # Deduplicate and sample balanced representation
    df_pairs = df_pairs.drop_duplicates(subset=["original", "simplified"]).reset_index(drop=True)
    
    # Save real scraped dataset
    df_pairs.to_csv("data/real_scraped_dataset.csv", index=False, encoding="utf-8")
    
    print(f"\nTotal Real-World Scraped Sentence Pairs Generated: {len(df_pairs)}")
    print("\nBreakdown by Language and Decision:")
    print(pd.crosstab(df_pairs["language"], df_pairs["decision"]))
    print("\nBreakdown by Domain:")
    print(df_pairs["domain"].value_counts())
    print("\nBreakdown by Error Category:")
    print(df_pairs["error_category"].value_counts())
    
    return df_pairs

if __name__ == "__main__":
    build_real_scraped_dataset()
