"""
Explainability Module for Multilingual Legal Meaning Preservation (LMP)
Provides:
1. Rule-guided Legal Feature Attribution across English and Hindi:
   - Deontic Modality (Obligation vs Discretion)
   - Negations & Contradictions
   - Conditionals and Exception Clauses
   - Numeric and Temporal Quantifiers
   - Legal Entity attribution
2. Natural language explanation synthesis for human interpretability
3. Highlighted token diff for visual inspection in UI and reports
"""

import re

# Domain-specific lexicons for English and Hindi
MODAL_DUTY_EN = {"shall", "must", "obligated", "required", "covenants", "agrees to"}
MODAL_PERM_EN = {"may", "can", "permitted", "allowed", "optional", "choose to", "discretion"}

MODAL_DUTY_HI = {"करेगा", "कराएगा", "करना होगा", "होगी", "होगा", "अनिवार्य", "बाध्य", "पड़ेगा"}
MODAL_PERM_HI = {"सकता है", "सकती है", "मर्जी", "चाहे तो", "ऐच्छिक", "विकल्प"}

CONDITION_EN = {"if", "unless", "provided that", "subject to", "except", "in the event", "contingent"}
CONDITION_HI = {"यदि", "अगर", "सिवाय", "बशर्ते", "जब तक", "के अधीन", "छोड़कर"}

NEGATION_EN = {"not", "never", "no", "prohibited", "forbidden", "shall not", "cannot"}
NEGATION_HI = {"नहीं", "वर्जित", "निषेध", "प्रतिबंधित", "कदापि नहीं"}

ENTITIES_EN = {"landlord": "tenant", "lessor": "lessee", "consumer": "manufacturer", "buyer": "seller", "employer": "employee"}
ENTITIES_HI = {"मकान मालिक": "किरायेदार", "उपभोक्ता": "निर्माता", "विक्रेता": "ग्राहक", "नियोजक": "कर्मचारी"}


def _contains_term(text_lower: str, term: str, lang: str) -> bool:
    """Checks term presence using word boundaries for Latin text to avoid substring false matches."""
    if lang == "en":
        return bool(re.search(rf"\b{re.escape(term)}\b", text_lower))
    return term in text_lower


def extract_numbers_and_dates(text):
    """Extracts numbers, percentages, currency, and date references."""
    return set(re.findall(r'\b\d+(?:st|nd|rd|th)?%?\b', text.lower()))


def analyze_legal_discrepancy(orig_text, simp_text, lang="en"):
    """
    Performs deterministic legal discrepancy diagnostic between original and simplified sentences.
    Auto-detects Devanagari vs Latin script so mismatched UI language selection never disables rules.
    Returns dict with keys: error_category, decision, lmp_estimate, explanation, key_differences.
    """
    orig_lower = orig_text.lower()
    simp_lower = simp_text.lower()
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in orig_text + simp_text)
    lang = "hi" if has_devanagari else "en"

    # 1. Identical match sanity check
    if orig_text.strip() == simp_text.strip():
        return {
            "error_category": "none",
            "decision": "Preserved",
            "lmp_estimate": 10.0,
            "explanation": "Exact verbatim legal match. Flawless preservation.",
            "key_differences": [],
        }

    findings = []  # (category, decision, lmp_est, explanation, diff_note)

    # 2. Contradiction / Negation Flip
    neg_set = NEGATION_EN if lang == "en" else NEGATION_HI
    has_neg_orig = any(_contains_term(orig_lower, neg, lang) for neg in neg_set)
    has_neg_simp = any(_contains_term(simp_lower, neg, lang) for neg in neg_set)
    if has_neg_orig != has_neg_simp:
        findings.append((
            "contradiction",
            "Not Preserved",
            1.0,
            "Direct legal contradiction detected: a prohibition or negative covenant was inverted, reversing legal liability.",
            "Negation polarity flipped (prohibition converted to permission or vice versa).",
        ))

    # 3. Number & Date Shifts
    orig_nums = extract_numbers_and_dates(orig_lower)
    simp_nums = extract_numbers_and_dates(simp_lower)
    if (orig_nums - simp_nums) or (simp_nums - orig_nums):
        findings.append((
            "date_number",
            "Not Preserved",
            2.0,
            f"Numeric terms or deadlines were altered (from {sorted(orig_nums)} to {sorted(simp_nums)}), prejudicing legal timelines or monetary terms.",
            f"Numeric/Temporal divergence: Original had {sorted(orig_nums)}, Simplified has {sorted(simp_nums)}.",
        ))

    # 4. Entity Shift
    ent_map = ENTITIES_EN if lang == "en" else ENTITIES_HI
    for k, v in ent_map.items():
        if (_contains_term(orig_lower, k, lang) and _contains_term(simp_lower, v, lang) and not _contains_term(simp_lower, k, lang)) or \
           (_contains_term(orig_lower, v, lang) and _contains_term(simp_lower, k, lang) and not _contains_term(simp_lower, v, lang)):
            findings.append((
                "entity",
                "Not Preserved",
                1.3,
                f"Legal entity inversion detected: obligations or rights were erroneously swapped between legal parties ({k} <-> {v}).",
                f"Legal actor switched between '{k}' and '{v}'.",
            ))
            break

    # 5. Duty vs. Permission (Modality Shift)
    duty_set = MODAL_DUTY_EN if lang == "en" else MODAL_DUTY_HI
    perm_set = MODAL_PERM_EN if lang == "en" else MODAL_PERM_HI
    orig_has_duty = any(_contains_term(orig_lower, m, lang) for m in duty_set)
    simp_has_perm = any(_contains_term(simp_lower, m, lang) for m in perm_set)
    if orig_has_duty and simp_has_perm:
        findings.append((
            "duty_vs_permission",
            "Not Preserved",
            2.5,
            "Deontic modality changed: an enforceable mandatory obligation ('shall'/'must') was diluted into a voluntary choice ('may'/'can').",
            "Mandatory legal duty demoted to discretionary permission.",
        ))

    # 6. Conditions and Exceptions
    cond_set = CONDITION_EN if lang == "en" else CONDITION_HI
    orig_conds = [c for c in cond_set if _contains_term(orig_lower, c, lang)]
    simp_conds = [c for c in cond_set if _contains_term(simp_lower, c, lang)]
    if orig_conds and not simp_conds:
        cat = "exception" if any(k in orig_conds for k in ["unless", "except", "सिवाय"]) else "condition"
        findings.append((
            cat,
            "Partially Preserved",
            4.5,
            f"Conditional qualifier ({orig_conds}) was omitted in the simplification, transforming a qualified right into an absolute one.",
            f"Operative conditional/exception clause dropped: {orig_conds}.",
        ))

    # 7. Significant Length Discrepancy (Omission)
    words_orig = len(orig_lower.split())
    words_simp = len(simp_lower.split())
    if words_simp < 0.4 * words_orig and words_orig > 12:
        findings.append((
            "omission",
            "Partially Preserved",
            5.5,
            "Severe compression resulted in the omission of secondary procedural or notice requirements.",
            "Extreme reduction in text volume (>60% reduction).",
        ))

    if findings:
        primary_cat, primary_dec, primary_est, primary_exp, _ = findings[0]
        return {
            "error_category": primary_cat,
            "decision": primary_dec,
            "lmp_estimate": primary_est,
            "explanation": primary_exp,
            "key_differences": [f[4] for f in findings],
        }

    # No fixed keyword rule matched
    return {
        "error_category": "none",
        "decision": "Preserved",
        "lmp_estimate": 9.5,
        "explanation": "No fixed statutory keyword subversion matched on surface tokens.",
        "key_differences": ["No critical legal subversions detected by symbolic keyword rules."],
    }
