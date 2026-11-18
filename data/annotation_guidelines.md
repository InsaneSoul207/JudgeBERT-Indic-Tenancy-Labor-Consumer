# Legal Meaning Preservation (LMP) Annotation Guidelines

## 1. Overview
Legal text simplification seeks to make dense, archaic legal provisions understandable to laypersons. However, conventional simplification metrics (BLEU, ROUGE, generic SBERT) evaluate surface or semantic similarity rather than legal enforceability. 

**Legal Meaning Preservation (LMP)** measures whether a simplified or reformulated sentence preserves the exact legal rights, duties, liabilities, conditions, exceptions, and procedural scope established in the original legal text.

---

## 2. LMP Scoring Scale (1 to 10)

LMP is scored on a continuous scale from **1.0 (Complete Subversion/Destruction of Meaning)** to **10.0 (Flawless Preservation of Legal Meaning)**.

### Categorical Decision Thresholds:
- **Preserved ($8.0 \le \text{Score} \le 10.0$)**:
  - The simplification successfully conveys the full operative legal effect of the original text.
  - Plain language substitutions (e.g., *"remit"* $\to$ *"pay"*, *"forthwith"* $\to$ *"immediately"*, *"व्यतीत"* $\to$ *"समाप्त"*) do not alter legal obligations or rights.
  - Grammatical reorganization retains all legal nuances, conditions, and parties.

- **Partially Preserved ($4.0 \le \text{Score} < 8.0$)**:
  - The core premise remains recognizable, but an auxiliary legal element has been modified or softened.
  - Examples: Omitting a non-critical notice method, slight ambiguity in procedural steps, minor changes in qualification terms without reversing legal liability.

- **Not Preserved ($1.0 \le \text{Score} < 4.0$)**:
  - The legal substance is materially distorted, reversed, eliminated, or fabricated.
  - Enforceability is breached: a duty is demoted to discretion, an essential condition or exception is dropped, dates/penalties are changed, or liability is flipped between parties.

---

## 3. The 9 Legal Failure Modes (Taxonomy)

When a sentence pair exhibits meaning divergence, annotators tag the primary error category:

1. **Omission (`omission`)**: A legally critical clause, liability exception, or qualifier present in the original sentence is dropped in the simplification.
2. **Hallucination (`hallucination`)**: The simplification introduces external facts, obligations, penalties, or covenants absent from the original clause.
3. **Contradiction (`contradiction`)**: Direct semantic or operational negation (e.g., *"shall not be liable"* $\to$ *"shall be liable"*).
4. **Duty vs. Permission (`duty_vs_permission`)**: Changing deontic modality (e.g., *"shall"* / *"must"* $\to$ *"may"* / *"can"* or vice-versa), turning mandatory obligations into discretionary acts.
5. **Conditions (`condition`)**: Altering or dropping conditional triggers (*"if"*, *"provided that"*, *"subject to"*).
6. **Exceptions (`exception`)**: Dropping or altering exclusionary clauses (*"unless"*, *"except in cases of"*, *"save as otherwise provided"*).
7. **Scope (`scope`)**: Widening or narrowing party jurisdiction (*"all residential tenants"* $\to$ *"any commercial tenant"*, *"exclusive jurisdiction"* $\to$ *"jurisdiction"*).
8. **Dates & Numbers (`date_number`)**: Distorting numeric thresholds, grace periods, limitation periods, interest rates, or currency values (*"within 30 days"* $\to$ *"within 3 months"*).
9. **Entities (`entity`)**: Misattributing rights or duties between legal parties (*"landlord"* $\leftrightarrow$ *"tenant"*, *"consumer"* $\leftrightarrow$ *"manufacturer"*).

---

## 4. Benchmark Scoring Rubric Table

| LMP Score Range | Decision | Description | Example |
| :---: | :---: | :--- | :--- |
| **9.0 – 10.0** | Preserved | Perfect legal equivalence; vocabulary simplified without loss of meaning. | *Orig:* "The Lessee shall remit payment by the 5th day of each calendar month."<br>*Simp:* "The tenant must pay rent by the 5th of each month." |
| **8.0 – 8.9** | Preserved | Minor stylistic rephrasing; negligible legal drift that does not impact rights/duties. | *Orig:* "All notices hereunder shall be in writing sent via registered post."<br>*Simp:* "Written notices must be sent by registered post." |
| **6.0 – 7.9** | Partially Preserved | Minor omission or slight ambiguity in procedural qualification, but primary obligation holds. | *Orig:* "Tenant must give written notice 30 days prior, delivered by hand or courier."<br>*Simp:* "Tenant must give 30 days written notice to landlord." |
| **4.0 – 5.9** | Partially Preserved | Meaning weakened; conditional or secondary safeguard dropped, but core action remains. | *Orig:* "Lessor shall repair structural defects within 14 days of written receipt."<br>*Simp:* "Landlord will repair structural defects as soon as notified." |
| **2.0 – 3.9** | Not Preserved | Substantial distortion of duty, date, scope, or liability. | *Orig:* "The tenant shall pay rent by the 5th, unless agreed otherwise in writing."<br>*Simp:* "The tenant may pay rent around the 5th of each month." |
| **1.0 – 1.9** | Not Preserved | Total legal contradiction, inversion of parties, or completely unrelated content. | *Orig:* "The manufacturer is strictly liable for consumer injury from defective goods."<br>*Simp:* "The consumer is responsible for any injury caused by defective goods." |

---

## 5. Sanity Check Anchors
- **Identical Pairs ($S_{orig} = S_{simp}$)**: Must always receive a deterministic score of **10.0** (Preserved).
- **Unrelated Pairs ($S_{orig} \neq S_{simp}$, random pairing across different statutory sections)**: Must always receive an LMP score of **1.0** (Not Preserved).
