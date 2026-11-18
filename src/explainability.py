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

MODAL_DUTY_HI = {"करेगा", "होगी", "होगा", "अनिवार्य", "बाध्य", "पड़ेगा"}
MODAL_PERM_HI = {"सकता है", "सकती है", "मर्जी", "चाहे तो", "ऐच्छिक", "विकल्प"}

CONDITION_EN = {"if", "unless", "provided that", "subject to", "except", "in the event", "contingent"}
CONDITION_HI = {"यदि", "अगर", "सिवाय", "बशर्ते", "जब तक", "के अधीन", "छोड़कर"}

NEGATION_EN = {"not", "never", "no", "prohibited", "forbidden", "shall not", "cannot"}
NEGATION_HI = {"नहीं", "वर्जित", "निषेध", "प्रतिबंधित", "कदापि नहीं"}

ENTITIES_EN = {"landlord": "tenant", "lessor": "lessee", "consumer": "manufacturer", "buyer": "seller"}
ENTITIES_HI = {"मकान मालिक": "किरायेदार", "उपभोक्ता": "निर्माता", "विक्रेता": "ग्राहक"}

def extract_numbers_and_dates(text):
    """Extracts numbers, percentages, currency, and date references."""
    # Match integers, decimals, ordinals (5th, 10th), and percent
    return set(re.findall(r'\b\d+(?:st|nd|rd|th)?%?\b', text.lower()))

def analyze_legal_discrepancy(orig_text, simp_text, lang="en"):
    """
    Performs deterministic legal discrepancy diagnostic between original and simplified sentences.
    Returns:
    - detected_error: Primary detected legal category
    - confidence: Diagnostic confidence
    - explanation: Human-readable legal rationale
    - key_differences: Detailed breakdown of affected legal facets
    """
    orig_lower = orig_text.lower()
    simp_lower = simp_text.lower()
    
    # 1. Check for identical match (Sanity)
    if orig_text.strip() == simp_text.strip():
        return {
            "error_category": "none",
            "decision": "Preserved",
            "lmp_estimate": 10.0,
            "explanation": "Exact verbatim legal match. Flawless preservation.",
            "key_differences": []
        }

    differences = []

    # 2. Number & Date Shifts
    orig_nums = extract_numbers_and_dates(orig_lower)
    simp_nums = extract_numbers_and_dates(simp_lower)
    dropped_nums = orig_nums - simp_nums
    added_nums = simp_nums - orig_nums
    
    if dropped_nums or added_nums:
        differences.append(f"Numeric/Temporal divergence: Original had {orig_nums}, Simplified has {simp_nums}.")
        return {
            "error_category": "date_number",
            "decision": "Not Preserved",
            "lmp_estimate": 2.0,
            "explanation": f"Numeric terms or deadlines were altered (from {list(orig_nums)} to {list(simp_nums)}), prejudicing legal timelines or monetary terms.",
            "key_differences": differences
        }

    # 3. Contradiction / Negation Flip
    has_neg_orig = any(neg in orig_lower for neg in (NEGATION_EN if lang == "en" else NEGATION_HI))
    has_neg_simp = any(neg in simp_lower for neg in (NEGATION_EN if lang == "en" else NEGATION_HI))
    if has_neg_orig != has_neg_simp:
        differences.append("Negation polarity flipped (prohibition converted to permission or vice versa).")
        return {
            "error_category": "contradiction",
            "decision": "Not Preserved",
            "lmp_estimate": 1.0,
            "explanation": "Direct legal contradiction detected: a prohibition or negative covenant was inverted, reversing legal liability.",
            "key_differences": differences
        }

    # 4. Duty vs. Permission (Modality Shift)
    duty_set = MODAL_DUTY_EN if lang == "en" else MODAL_DUTY_HI
    perm_set = MODAL_PERM_EN if lang == "en" else MODAL_PERM_HI
    
    orig_has_duty = any(m in orig_lower for m in duty_set)
    simp_has_perm = any(m in simp_lower for m in perm_set)
    
    if orig_has_duty and simp_has_perm:
        differences.append("Mandatory legal duty demoted to discretionary permission.")
        return {
            "error_category": "duty_vs_permission",
            "decision": "Not Preserved",
            "lmp_estimate": 2.5,
            "explanation": "Deontic modality changed: an enforceable mandatory obligation ('shall'/'must') was diluted into a voluntary choice ('may'/'can').",
            "key_differences": differences
        }

    # 5. Conditions and Exceptions
    cond_set = CONDITION_EN if lang == "en" else CONDITION_HI
    orig_conds = [c for c in cond_set if c in orig_lower]
    simp_conds = [c for c in cond_set if c in simp_lower]
    
    if orig_conds and not simp_conds:
        differences.append(f"Operative conditional/exception clause dropped: {orig_conds}.")
        return {
            "error_category": "exception" if any(k in orig_conds for k in ["unless", "except", "सिवाय"]) else "condition",
            "decision": "Partially Preserved",
            "lmp_estimate": 4.5,
            "explanation": f"Conditional qualifier ({orig_conds}) was omitted in the simplification, transforming a qualified right into an absolute one.",
            "key_differences": differences
        }

    # 6. Entity Shift
    ent_map = ENTITIES_EN if lang == "en" else ENTITIES_HI
    for k, v in ent_map.items():
        if (k in orig_lower and v in simp_lower and k not in simp_lower) or \
           (v in orig_lower and k in simp_lower and v not in simp_lower):
            differences.append(f"Legal actor switched between '{k}' and '{v}'.")
            return {
                "error_category": "entity",
                "decision": "Not Preserved",
                "lmp_estimate": 1.3,
                "explanation": f"Legal entity inversion detected: obligations or rights were erroneously swapped between legal parties ({k} <-> {v}).",
                "key_differences": differences
            }

    # 7. Significant Length Discrepancy (Omission or Hallucination)
    words_orig = len(orig_lower.split())
    words_simp = len(simp_lower.split())
    if words_simp < 0.4 * words_orig and words_orig > 12:
        differences.append("Extreme reduction in text volume (>60% reduction).")
        return {
            "error_category": "omission",
            "decision": "Partially Preserved",
            "lmp_estimate": 5.5,
            "explanation": "Severe compression resulted in the omission of secondary procedural or notice requirements.",
            "key_differences": differences
        }

    # If no severe divergence is found
    return {
        "error_category": "none",
        "decision": "Preserved",
        "lmp_estimate": 9.5,
        "explanation": "The core operative legal meaning, rights, duties, and conditions are faithfully preserved.",
        "key_differences": ["No critical legal subversions detected."]
    }
