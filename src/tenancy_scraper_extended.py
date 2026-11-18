"""
Extended Tenancy‑Only Scraper

Adds additional Indian state tenancy statutes and related legal sources to the
baseline scraper (src/scraper.py). The script re‑uses the helper functions
`clean_text`, `scrape_prs_page`, and `scrape_wikipedia_hindi` defined in the
original scraper.

It generates a CSV `data/tenancy_extended_dataset.csv` containing only the
Tenancy domain (English + Hindi) pairs.
"""
import os, re, pandas as pd
from scraper import clean_text, scrape_prs_page, scrape_wikipedia_hindi

def build_extended_tenancy_dataset():
    print("=" * 70)
    print("EXTENDED TENANCY SCRAPER – ADDING STATE‑LEVEL ACTS")
    print("=" * 70)

    raw_items = []

    # 1. National Model Tenancy Act (already scraped in base, but include for completeness)
    raw_items.extend(scrape_prs_page(
        "https://prsindia.org/billtrack/the-model-tenancy-act-2021", "tenancy"
    ))

    # 2. State‑specific tenancy statutes (public PRS pages where available)
    state_urls = {
        "Karnataka Tenancy Act 2019": "https://prsindia.org/billtrack/karnataka-tenancy-act-2019",
        "Maharashtra Rent Control Act 1999": "https://prsindia.org/billtrack/maharashtra-rent-control-act-1999",
        "Delhi Rent Control Act 1958": "https://prsindia.org/billtrack/delhi-rent-control-act-1958",
        "West Bengal Tenancy Act 1995": "https://prsindia.org/billtrack/west-bengal-tenancy-act-1995",
    }
    for name, url in state_urls.items():
        raw_items.extend(scrape_prs_page(url, "tenancy"))

    # 3. Hindi Wikipedia pages for state tenancy acts (if existent)
    hindi_pages = [
        "कर्नाटक किरायेदार अधिनियम 2019",
        "महाराष्ट्र किराया नियंत्रण अधिनियम 1999",
        "दिल्ली किराया नियंत्रण अधिनियम 1958",
        "पश्चिम बंगाल किरायेदारी अधिनियम 1995",
    ]
    for title in hindi_pages:
        raw_items.extend(scrape_wikipedia_hindi(title, "tenancy"))

    # 4. Additional generic tenancy‑related sections from Transfer of Property Act (Hindi)
    raw_items.extend(scrape_wikipedia_hindi("सम्पत्ति अन्तरण अधिनियम १८८२", "tenancy"))
    raw_items.extend(scrape_wikipedia_hindi("किराया अधिनियम", "tenancy"))

    print(f"\nCollected raw clauses: {len(raw_items)}")

    # ------------------------------------------------------------------
    # Pair generation – reuse same logic as the base scraper for consistency
    # ------------------------------------------------------------------
    pairs = []
    pair_id = 1
    for item in raw_items:
        orig = item["text"]
        dom = item["domain"]
        # 1. Preserved – plain‑language re‑write (very light, keep original for now)
        simp_preserved = orig
        pairs.append({
            "id": f"EXT-EN-{pair_id:04d}" if item["language"] == "en" else f"EXT-HI-{pair_id:04d}",
            "language": item["language"],
            "domain": dom,
            "original": orig,
            "simplified": simp_preserved,
            "lmp_score": 9.6,
            "decision": "Preserved",
            "error_category": "none",
            "source_url": item["source_url"],
            "explanation": "Direct clause retained unchanged – serves as a preserved baseline."
        })
        pair_id += 1

        # 2. Duty vs Permission – simple heuristic
        if any(w in orig.lower() for w in ["requires", "must", "shall", "mandates", "prohibits"]):
            simp_duty = orig
            for src, tgt in [
                ("requires", "suggests that"),
                ("must", "may consider whether to"),
                ("shall", "can optionally"),
                ("mandates", "recommends"),
                ("prohibits", "advises against")
            ]:
                simp_duty = simp_duty.replace(src, tgt)
            pairs.append({
                "id": f"EXT-EN-{pair_id:04d}" if item["language"] == "en" else f"EXT-HI-{pair_id:04d}",
                "language": item["language"],
                "domain": dom,
                "original": orig,
                "simplified": simp_duty,
                "lmp_score": 2.5,
                "decision": "Not Preserved",
                "error_category": "duty_vs_permission",
                "source_url": item["source_url"],
                "explanation": "Statutory duty demoted to discretionary option."
            })
            pair_id += 1

    # Save CSV
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(pairs)
    out_path = "data/tenancy_extended_dataset.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nSaved extended tenancy dataset: {len(df)} rows -> {out_path}")

if __name__ == "__main__":
    build_extended_tenancy_dataset()
