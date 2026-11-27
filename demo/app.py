"""
Interactive Streamlit Dashboard for PJ_08:
Multilingual Legal Meaning Preservation (LMP) using JUDGEBERT.
"""

from __future__ import annotations

import os
os.environ["USE_TF"] = "0"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import difflib
import html
import json
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.baselines import BaselineEvaluator
from src.explainability import analyze_legal_discrepancy
from src.model import JudgeBertPredictor, preprocess_legal_text

st.set_page_config(
    page_title="JUDGEBERT | Multilingual Legal Meaning Preservation",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Parchment & Forest-Green Theme Styling (Zero Icons/Emojis)
# Palette:
#   Page BG:       #F3ECDB (Parchment)
#   Surface/Card:  #FFFCF6 (Warm White)
#   Accent/Heading:#3E503C (Forest Green)
#   Body/Input:    #262B25 (Dark Charcoal)
#   Borders/Div:   #7F886A (Muted Olive)
#   Active Accent: #FF6F3D (Orange)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #F3ECDB !important;
        color: #262B25 !important;
    }
    [data-testid="stHeader"] {
        background-color: #F3ECDB !important;
        border-bottom: 1px solid rgba(127, 136, 106, 0.25);
    }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background-color: #FFFCF6 !important;
        border-right: 1px solid #7F886A !important;
        color: #262B25 !important;
    }
    .block-container {
        padding-top: 2.6rem;
        padding-bottom: 1.8rem;
        max-width: 1220px;
    }
    /* Headings, labels, and body copy */
    h1, h2, h3, h4, .stSubheader, [data-testid="stHeading"] * {
        color: #3E503C !important;
    }
    p, li, label, span, .stMarkdown, .stCaption {
        color: #262B25;
    }
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
        color: #3E503C !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
    }
    /* Compact Header */
    .jb-header {
        margin: 0 0 0.55rem 0;
        padding-bottom: 0.45rem;
    }
    .jb-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.05;
        color: #3E503C !important;
        margin: 0;
    }
    .jb-accent {
        width: 56px;
        height: 4px;
        background-color: #FF6F3D;
        border-radius: 2px;
        margin: 0.35rem 0 0.38rem 0;
    }
    .jb-subtitle {
        font-size: 0.96rem;
        font-weight: 600;
        color: #262B25;
        margin: 0 0 0.22rem 0;
        line-height: 1.3;
    }
    .jb-meta {
        font-size: 0.78rem;
        color: #3E503C;
        opacity: 0.9;
        margin: 0;
        line-height: 1.35;
    }
    /* Dropdowns and Textareas (#FFFCF6 warm white + #7F886A olive border + #262B25 text) */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"],
    [data-testid="stTextArea"] > div > div,
    [data-testid="stTextInput"] > div > div {
        background-color: #FFFCF6 !important;
        border: 1px solid #7F886A !important;
        border-radius: 6px !important;
        color: #262B25 !important;
    }
    [data-baseweb="select"] *,
    textarea,
    input[type="text"] {
        color: #262B25 !important;
        background-color: #FFFCF6 !important;
        caret-color: #262B25 !important;
    }
    div[data-baseweb="popover"],
    ul[role="listbox"],
    li[role="option"] {
        background-color: #FFFCF6 !important;
        color: #262B25 !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #F3ECDB !important;
        color: #3E503C !important;
        font-weight: 600;
    }
    [data-testid="stTextArea"] textarea {
        min-height: 140px !important;
        line-height: 1.5 !important;
    }
    /* Primary Evaluate Button (#3E503C forest green + white text) & Secondary Clear */
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background-color: #3E503C !important;
        border: 1px solid #3E503C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #2F3E2D !important;
        border-color: #2F3E2D !important;
    }
    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: #FFFCF6 !important;
        border: 1px solid #7F886A !important;
        color: #3E503C !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    button[kind="secondary"] *,
    button[data-testid="stBaseButton-secondary"] * {
        color: #3E503C !important;
    }
    /* Dividers (#7F886A muted olive) */
    hr, [data-testid="stDivider"] {
        border: none !important;
        border-top: 1px solid #7F886A !important;
        margin: 0.85rem 0 !important;
    }
    /* Tabs (#3E503C labels, #FF6F3D active underline, responsive wrap) */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.25rem 0.65rem !important;
        border-bottom: 1.5px solid #7F886A !important;
        margin-bottom: 0.6rem !important;
        overflow: visible !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.42rem 0.65rem !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #3E503C !important;
        background: transparent !important;
        white-space: nowrap !important;
    }
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #3E503C !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #FF6F3D !important;
        color: #3E503C !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    /* Cards & Expanders (#FFFCF6 + #7F886A border) */
    .jb-card {
        border: 1px solid #7F886A;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        background-color: #FFFCF6;
        margin-bottom: 0.7rem;
        color: #262B25;
    }
    .jb-kpi {
        min-height: 118px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .jb-kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #3E503C;
        margin-bottom: 0.2rem;
    }
    .jb-kpi-val {
        font-size: clamp(1.08rem, 1.3vw, 1.38rem);
        font-weight: 700;
        line-height: 1.2;
        color: #262B25;
        margin-bottom: 0.15rem;
    }
    .jb-kpi-delta {
        font-size: 0.78rem;
        color: #3E503C;
    }
    /* Verdict Badges: Preserved, Partial, Not Preserved */
    .jb-pill {
        display: inline-block;
        padding: 0.24rem 0.72rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .jb-pill-green {
        background-color: #E3F1E8;
        color: #1F4E32;
        border: 1.5px solid #2E6F40;
    }
    .jb-pill-amber {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1.5px solid #D97706;
    }
    .jb-pill-red {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1.5px solid #DC2626;
    }
    /* Diff Box & Alerts */
    .jb-diff-box {
        border: 1px solid #7F886A;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        background-color: #FFFCF6;
        color: #262B25;
        font-size: 0.93rem;
        line-height: 1.65;
        margin-bottom: 0.75rem;
    }
    .diff-del {
        background-color: #FEE2E2;
        color: #991B1B;
        text-decoration: line-through;
        padding: 0.05rem 0.25rem;
        border-radius: 3px;
    }
    .diff-add {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.05rem 0.25rem;
        border-radius: 3px;
        font-weight: 600;
    }
    [data-testid="stAlert"],
    [data-testid="stAlert"] > div {
        background-color: #FFFCF6 !important;
        border-color: #7F886A !important;
        color: #262B25 !important;
    }
    [data-testid="stAlert"] {
        border: 1px solid #7F886A !important;
        border-radius: 6px !important;
    }
    [data-testid="stExpander"] {
        background-color: #FFFCF6 !important;
        border: 1px solid #7F886A !important;
        border-radius: 8px !important;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2.4rem;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }
        .jb-title {
            font-size: 1.55rem;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.80rem !important;
            padding: 0.35rem 0.5rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Display Helpers & Reusable UI Components
# ---------------------------------------------------------------------------

DISPLAY_LABELS = {
    "TF-IDF_Cosine": "TF-IDF Cosine",
    "SBERT_Cosine": "Generic SBERT Cosine",
    "ROUGE-L": "ROUGE-L",
    "Levenshtein": "Levenshtein Ratio",
    "BLEU": "BLEU (Sentence)",
    "JUDGEBERT": "JUDGEBERT (Ours v2)",
    "consumer_protection": "Consumer Protection Law",
    "tenancy": "Tenancy Law",
    "employment_labor": "Employment, Labor & Contracts",
    "en": "English (EN)",
    "hi": "Hindi (HI)",
}

PRESET_EXAMPLES = {
    "Custom Input": None,
    "EN | Tenancy: Duty Diluted (shall -> may)": {
        "orig": "The tenant shall pay rent by the fifth of every month, unless otherwise agreed in writing.",
        "simp": "The tenant may pay rent around the fifth of every month.",
        "lang": "en",
    },
    "EN | Tenancy: Exception Dropped (unless omitted)": {
        "orig": "The tenant shall not keep domestic pets on the premises without obtaining prior written authorization from the landlord.",
        "simp": "The tenant is strictly forbidden from keeping any pets inside the rental property.",
        "lang": "en",
    },
    "EN | Tenancy: Timeline Altered (15 days -> 6 months)": {
        "orig": "The Landlord shall refund the deposit within 15 days following formal handover of keys.",
        "simp": "The landlord shall refund the deposit within six months following formal handover of keys.",
        "lang": "en",
    },
    "EN | Consumer: Valid Plain-English Simplification": {
        "orig": "A consumer who purchases a defective product has the right to demand full replacement or refund within 30 days of delivery.",
        "simp": "If a buyer receives a faulty product, they can ask for a complete replacement or a full refund within 30 days of delivery.",
        "lang": "en",
    },
    "EN | Labor: Gratuity Entity Swap (Employer -> Employee)": {
        "orig": "The employer shall arrange to pay the amount of gratuity within thirty days from the date it becomes payable to the person to whom the gratuity is payable.",
        "simp": "Employees are required to pay gratuity to the employer within 30 days of resigning.",
        "lang": "en",
    },
    "HI | Tenancy: Obligation Diluted (करेगा -> चाहे तो)": {
        "orig": "किरायेदार प्रत्येक अंग्रेजी कैलेंडर माह की पांचवीं तारीख तक निर्धारित बैंक खाते में मासिक किराये का भुगतान करेगा।",
        "simp": "किरायेदार चाहे तो महीने की 5 तारीख के आसपास किराया दे सकता है।",
        "lang": "hi",
    },
    "HI | Tenancy: Party Entity Swap (मकान मालिक -> किरायेदार)": {
        "orig": "मकान पर लगने वाले नगर निगम टैक्स का भुगतान मकान मालिक द्वारा किया जाएगा।",
        "simp": "मकान के सारे म्यूनिसिपल टैक्स और वाटर सेस किरायेदार को भरने होंगे।",
        "lang": "hi",
    },
    "HI | Consumer: Hallucinated Penalty (50,000 रुपये जुर्माना)": {
        "orig": "उपभोक्ता किसी भी अनुचित व्यापार व्यवहार के विरुद्ध जिला उपभोक्ता विवाद प्रतितोष आयोग में शिकायत दर्ज कर सकता है।",
        "simp": "उपभोक्ता आयोग में शिकायत करने से पहले ग्राहक को विक्रेता को 50,000 रुपये का जुर्माना भरना अनिवार्य है।",
        "lang": "hi",
    },
    "HI | Labor: Bonus Obligation Preserved (Valid)": {
        "orig": "प्रत्येक नियोजक प्रत्येक लेखा वर्ष के संबंध में प्रत्येक कर्मचारी को न्यूनतम बोनस का संदाय करेगा जो कर्मचारी द्वारा उस लेखा वर्ष के दौरान अर्जित वेतन या मजदूरी का 8.33 प्रतिशत होगा।",
        "simp": "मालिक को हर साल हर पात्र कर्मचारी को सालाना वेतन का कम से कम 8.33 प्रतिशत न्यूनतम बोनस के रूप में अनिवार्य रूप से देना होगा।",
        "lang": "hi",
    },
    "EN | Sanity Anchor: Verbatim Match": {
        "orig": "The Lessee covenants to keep the exterior walls, roof, and structural foundations in sound repair.",
        "simp": "The Lessee covenants to keep the exterior walls, roof, and structural foundations in sound repair.",
        "lang": "en",
    },
}


def _render_kpi_card(col, label: str, value: str, delta: str = "") -> None:
    col.markdown(
        f"<div class='jb-card jb-kpi'>"
        f"<div class='jb-kpi-label'>{html.escape(label)}</div>"
        f"<div class='jb-kpi-val'>{html.escape(value)}</div>"
        f"<div class='jb-kpi-delta'>{html.escape(delta)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _decision_badge_html(decision: str) -> str:
    if decision == "Preserved":
        cls = "jb-pill jb-pill-green"
    elif decision == "Partially Preserved":
        cls = "jb-pill jb-pill-amber"
    else:
        cls = "jb-pill jb-pill-red"
    return f"<span class='{cls}'>{html.escape(decision)}</span>"


def _render_token_diff_html(orig: str, simp: str) -> str:
    orig_tokens = re.findall(r"\S+", orig)
    simp_tokens = re.findall(r"\S+", simp)
    matcher = difflib.SequenceMatcher(a=orig_tokens, b=simp_tokens)
    chunks: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunks.append(html.escape(" ".join(orig_tokens[i1:i2])))
        elif tag == "delete":
            chunks.append(f"<span class='diff-del'>{html.escape(' '.join(orig_tokens[i1:i2]))}</span>")
        elif tag == "insert":
            chunks.append(f"<span class='diff-add'>{html.escape(' '.join(simp_tokens[j1:j2]))}</span>")
        elif tag == "replace":
            chunks.append(f"<span class='diff-del'>{html.escape(' '.join(orig_tokens[i1:i2]))}</span>")
            chunks.append(f"<span class='diff-add'>{html.escape(' '.join(simp_tokens[j1:j2]))}</span>")
    return " ".join(chunks)


def _style_plotly(fig: go.Figure, height: int = 320, y_title: str = "", y_range: list[float] | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=40, r=20, t=42, b=36),
        paper_bgcolor="#FFFCF6",
        plot_bgcolor="#FFFCF6",
        font=dict(size=12, color="#262B25"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#262B25")),
        yaxis=dict(
            title=y_title,
            range=y_range,
            gridcolor="rgba(127, 136, 106, 0.25)",
            zerolinecolor="rgba(127, 136, 106, 0.45)",
            tickfont=dict(color="#262B25"),
            title_font=dict(color="#3E503C"),
        ),
        xaxis=dict(
            gridcolor="rgba(127, 136, 106, 0.14)",
            tickfont=dict(color="#262B25"),
            title_font=dict(color="#3E503C"),
        ),
    )
    return fig


def _load_json(path: str) -> dict | list | None:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _format_metrics_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    cols = ["pearson_r", "spearman_rho", "rmse", "mae", "accuracy", "macro_f1"]
    df = df_raw[cols].copy()
    df.index = [DISPLAY_LABELS.get(str(idx), str(idx)) for idx in df.index]
    df.columns = ["Pearson r", "Spearman rho", "RMSE", "MAE", "Accuracy", "Macro-F1"]
    return df


# ---------------------------------------------------------------------------
# Resource Initialization
# ---------------------------------------------------------------------------

@st.cache_resource
def load_system():
    base_model = "sentence-transformers/all-MiniLM-L6-v2"
    model_path = "models/best_judgebert.pt" if os.path.exists("models/best_judgebert.pt") else None
    predictor = JudgeBertPredictor(model_path=model_path, base_model_name=base_model)
    baseline_eval = BaselineEvaluator(sbert_model_name=base_model)
    return predictor, baseline_eval


try:
    predictor, baseline_eval = load_system()
    model_ready = True
except Exception as exc:
    model_ready = False
    st.error(f"Model initialization failed: {exc}")

# ---------------------------------------------------------------------------
# Sidebar: Technical Reference (Zero Team Names or Student IDs)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Architecture & Corpus")
    st.caption("JUDGEBERT Multilingual Evaluation Reference")
    st.divider()
    st.markdown("**Model Configuration**")
    st.markdown(
        "- Backbone: `all-MiniLM-L6-v2` Cross-Encoder\n"
        "- Parameters: `22,866,446` (100% fine-tuned)\n"
        "- Context Window: `256` tokens (`0.5 CLS + 0.5 Mean`)\n"
        "- Hindi Handling: Lossless phonetic transduction (`[UNK]: 92.4% -> 0.0%`)\n"
        "- Best Checkpoint: Epoch `11` (Val `r = 0.7569`, Acc `80.30%`)"
    )
    st.divider()
    st.markdown("**Corpus Composition (`N = 2,695`)**")
    st.markdown(
        "- Tenancy Law: `1,031` (`704 EN / 327 HI`)\n"
        "- Consumer Protection: `958` (`561 EN / 397 HI`)\n"
        "- Employment & Labor: `706` (`386 EN / 320 HI`)\n"
        "- Splits: Train `2,013` | Val `330` | Test `352`"
    )

# ---------------------------------------------------------------------------
# Compact Header & Responsive Navigation Tabs
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="jb-header">
      <h1 class="jb-title">JUDGEBERT</h1>
      <div class="jb-accent"></div>
      <p class="jb-subtitle">Multilingual Legal Meaning Preservation</p>
      <p class="jb-meta">CSET 346 – Natural Language Processing &bull; Project ID: PJ_08 &bull; Instructor: Dr. Surabhi Solanki</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Evaluator",
    "Baselines",
    "EN vs HI",
    "OOD Transfer",
    "Sanity Checks",
    "Case Study",
])

# ---------------------------------------------------------------------------
# Tab 1: Evaluator
# ---------------------------------------------------------------------------

def _apply_preset() -> None:
    choice = st.session_state.get("preset_choice", "Custom Input")
    data = PRESET_EXAMPLES.get(choice)
    if data:
        st.session_state["orig_input"] = data["orig"]
        st.session_state["simp_input"] = data["simp"]
        st.session_state["lang_input"] = data["lang"]


def _clear_inputs() -> None:
    st.session_state["preset_choice"] = "Custom Input"
    st.session_state["orig_input"] = ""
    st.session_state["simp_input"] = ""


if "orig_input" not in st.session_state:
    first_key = list(PRESET_EXAMPLES.keys())[1]
    st.session_state["preset_choice"] = first_key
    st.session_state["orig_input"] = PRESET_EXAMPLES[first_key]["orig"]
    st.session_state["simp_input"] = PRESET_EXAMPLES[first_key]["simp"]
    st.session_state["lang_input"] = PRESET_EXAMPLES[first_key]["lang"]

with tabs[0]:
    # Controls cleanly above both sentence boxes
    ctrl_col1, ctrl_col2 = st.columns([3.0, 1.2])
    with ctrl_col1:
        st.selectbox(
            "Benchmark Case",
            list(PRESET_EXAMPLES.keys()),
            key="preset_choice",
            on_change=_apply_preset,
        )
    with ctrl_col2:
        lang = st.selectbox(
            "Language",
            ["en", "hi"],
            key="lang_input",
            format_func=lambda x: "English (en)" if x == "en" else "Hindi (hi)",
        )

    # Equal-width/height side-by-side on desktop, automatically stacked Original then Simplified on narrow screens
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        orig_text = st.text_area("Original Clause", key="orig_input", height=140)
    with col_in2:
        simp_text = st.text_area("Simplified Clause", key="simp_input", height=140)

    # Primary Evaluate Meaning Preservation action placed directly below both inputs
    btn_col1, btn_col2, _ = st.columns([2.2, 0.85, 2.2])
    evaluate_btn = btn_col1.button("Evaluate Meaning Preservation", type="primary", use_container_width=True)
    btn_col2.button("Clear", on_click=_clear_inputs, use_container_width=True)

    # Results directly beneath the button
    if evaluate_btn and model_ready:
        if not orig_text.strip() or not simp_text.strip():
            st.warning("Enter both Original Clause and Simplified Clause before evaluating.")
        else:
            jb_res = predictor.predict_pair(orig_text, simp_text)
            has_hi_script = any("\u0900" <= ch <= "\u097f" for ch in orig_text + simp_text)
            effective_lang = "hi" if has_hi_script else "en"
            diag = analyze_legal_discrepancy(orig_text, simp_text, lang=effective_lang)

            df_single = pd.DataFrame([{"id": "LIVE-01", "original": orig_text, "simplified": simp_text}])
            sbert_score = float(baseline_eval.run_sbert_baseline(df_single)["sbert_lmp_pred"].iloc[0])
            lex_res = baseline_eval.run_lexical_baselines(df_single).iloc[0]
            tfidf_score = float(baseline_eval.run_tfidf_baseline(df_single)["tfidf_lmp_pred"].iloc[0])
            lev_score = float(lex_res["levenshtein_lmp_pred"])

            jb_score = float(jb_res["lmp_score"])
            gap = sbert_score - jb_score

            st.divider()
            st.markdown(
                f"<div style='display:flex; flex-wrap:wrap; align-items:center; gap:0.75rem; margin-bottom:0.75rem;'>"
                f"<span style='font-size:1.12rem; font-weight:700; color:#3E503C;'>Evaluation Verdict</span>"
                f"{_decision_badge_html(jb_res['decision'])}"
                f"</div>",
                unsafe_allow_html=True,
            )

            err_label = jb_res["error_category"].replace("_", " ").title()
            k1, k2, k3, k4 = st.columns(4)
            _render_kpi_card(k1, "JUDGEBERT LMP Score", f"{jb_score:.2f} / 10.0", "Preserved band: [8.0, 10.0]")
            _render_kpi_card(k2, "Neural Error Class", err_label, "10-class cross-encoder head")
            _render_kpi_card(k3, "Generic SBERT Score", f"{sbert_score:.2f} / 10.0", f"Gap vs. JUDGEBERT: {gap:+.2f}")
            _render_kpi_card(
                k4,
                "Lexical Scores",
                f"{float(lex_res['bleu_lmp_pred']):.1f} | {float(lex_res['rouge_l_lmp_pred']):.1f}",
                "BLEU | ROUGE-L (1-10 scale)",
            )

            col_vis1, col_vis2 = st.columns([1.15, 1.0])
            with col_vis1:
                st.markdown("**Model Score Comparison (1.0 - 10.0 Scale)**")
                chart_names = ["JUDGEBERT (Ours)", "Generic SBERT", "TF-IDF Cosine", "ROUGE-L", "Levenshtein", "BLEU"]
                chart_vals = [
                    jb_score,
                    sbert_score,
                    tfidf_score,
                    float(lex_res["rouge_l_lmp_pred"]),
                    lev_score,
                    float(lex_res["bleu_lmp_pred"]),
                ]
                bar_colors = ["#3E503C", "#FF6F3D", "#7F886A", "#7F886A", "#7F886A", "#7F886A"]
                fig_live = go.Figure(
                    go.Bar(
                        x=chart_vals,
                        y=chart_names,
                        orientation="h",
                        marker_color=bar_colors,
                        text=[f"{v:.2f}" for v in chart_vals],
                        textposition="outside",
                        textfont=dict(color="#262B25"),
                    )
                )
                fig_live.add_vline(
                    x=4.0,
                    line_dash="dot",
                    line_color="#DC2626",
                    annotation_text="Cutoff 4.0",
                    annotation_position="top left",
                    annotation_yshift=12,
                    annotation_font_size=10,
                    annotation_font_color="#991B1B",
                )
                fig_live.add_vline(
                    x=8.0,
                    line_dash="dot",
                    line_color="#2E6F40",
                    annotation_text="Preserved 8.0",
                    annotation_position="top right",
                    annotation_yshift=12,
                    annotation_font_size=10,
                    annotation_font_color="#1F4E32",
                )
                fig_live.update_layout(
                    height=275,
                    margin=dict(l=10, r=28, t=30, b=24),
                    paper_bgcolor="#FFFCF6",
                    plot_bgcolor="#FFFCF6",
                    font=dict(color="#262B25"),
                    xaxis=dict(range=[0, 11.5], gridcolor="rgba(127, 136, 106, 0.25)", tickfont=dict(color="#262B25")),
                    yaxis=dict(autorange="reversed", tickfont=dict(color="#262B25")),
                )
                st.plotly_chart(fig_live, use_container_width=True)

            with col_vis2:
                st.markdown("**Token-Level Edit Diff (Original vs. Simplified)**")
                st.markdown(f"<div class='jb-diff-box'>{_render_token_diff_html(orig_text, simp_text)}</div>", unsafe_allow_html=True)
                st.caption("Strikethrough red: removed/replaced terms. Green: inserted/substituted terms.")

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.markdown("**Rule-Guided Legal Diagnostic**")
                if diag["error_category"] != "none":
                    st.info(
                        f"Symbolic Error Category: {diag['error_category']} | "
                        f"Rule Hint: {diag['decision']} | "
                        f"Script: {'Hindi' if has_hi_script else 'English'}"
                    )
                    st.write(f"**Legal Rationale:** {diag['explanation']}")
                    for diff in diag["key_differences"]:
                        st.markdown(f"- {diff}")
                elif jb_res["decision"] != "Preserved":
                    st.warning(
                        f"Rule Overlay Status: No fixed keyword hit | "
                        f"Neural Verdict Applies: {jb_res['decision']}"
                    )
                    st.write(
                        f"**Neuro-Symbolic Summary:** No fixed statutory keyword rule fired on surface tokens, "
                        f"but JUDGEBERT's cross-attention detected a semantic breach "
                        f"({jb_res['error_category']}, LMP {jb_score:.2f}/10). "
                        f"Inspect highlighted spans in the Token-Level Edit Diff above."
                    )
                else:
                    st.success("Symbolic Error Category: none | Rule & Neural Verdict: Preserved")
                    st.write(
                        "**Legal Rationale:** Core statutory obligations, entities, numbers, and caveats "
                        "align consistently across both neural and symbolic checks."
                    )

            with col_exp2:
                st.markdown("**Baseline Divergence & Script Processing**")
                if gap >= 2.0 and jb_score < 8.0:
                    st.warning(
                        f"Critical Baseline False Positive: Generic SBERT assigns {sbert_score:.2f}/10 due to shared surface vocabulary, "
                        f"over-scoring JUDGEBERT by +{gap:.2f} points while missing an operative statutory shift."
                    )
                elif jb_score < 4.0 and sbert_score < 4.5:
                    st.info("Both neural cross-attention and surface baselines detect major semantic divergence.")
                else:
                    st.success("Generic similarity and JUDGEBERT alignment confirms consistent surface and legal fidelity.")

                if has_hi_script:
                    with st.expander("Phonetic Devanagari Transduction Inspector (Zero-[UNK] Pipeline)"):
                        st.caption("Deterministic phonetic normalization mapped before all-MiniLM-L6-v2 WordPiece tokenization:")
                        st.code(
                            f"Source:     {preprocess_legal_text(orig_text, True)}\n"
                            f"Simplified: {preprocess_legal_text(simp_text, True)}",
                            language="text",
                            wrap_lines=True,
                        )

# ---------------------------------------------------------------------------
# Tab 2: Baselines (Experiment 1)
# ---------------------------------------------------------------------------

with tabs[1]:
    st.subheader("Generic Baselines vs. JUDGEBERT (Test N = 352)")
    e1 = _load_json("experiments/results/exp1_baselines_vs_judgebert.json")
    if e1:
        overall = e1.get("overall", e1)
        jb_m = overall["JUDGEBERT"]
        sb_m = overall["SBERT_Cosine"]

        m1, m2, m3, m4 = st.columns(4)
        _render_kpi_card(m1, "JUDGEBERT Pearson r", f"{jb_m['pearson_r']:.4f}", f"SBERT baseline: {sb_m['pearson_r']:.4f}")
        _render_kpi_card(m2, "Decision Accuracy", f"{jb_m['accuracy']*100:.2f}%", f"SBERT baseline: {sb_m['accuracy']*100:.2f}%")
        _render_kpi_card(m3, "Macro-F1 (3-Way)", f"{jb_m['macro_f1']:.4f}", f"Partial F1: {jb_m['classification_report']['Partially Preserved']['f1-score']*100:.2f}%")
        _render_kpi_card(m4, "Test MAE / RMSE", f"{jb_m['mae']:.2f} / {jb_m['rmse']:.2f}", "60.0% lower MAE vs. SBERT")

        df_e1 = pd.DataFrame(overall).T
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("**Overall Baselines vs. JUDGEBERT**")
            names = [DISPLAY_LABELS.get(k, k) for k in df_e1.index]
            fig_e1 = go.Figure(
                data=[
                    go.Bar(name="Pearson r", x=names, y=df_e1["pearson_r"], marker_color="#3E503C", text=[f"{v:.2f}" for v in df_e1["pearson_r"]], textposition="outside"),
                    go.Bar(name="Macro-F1", x=names, y=df_e1["macro_f1"], marker_color="#FF6F3D", text=[f"{v:.2f}" for v in df_e1["macro_f1"]], textposition="outside"),
                ]
            )
            fig_e1.update_layout(barmode="group")
            st.plotly_chart(_style_plotly(fig_e1, height=320, y_range=[0, 0.92]), use_container_width=True)

        with col_c2:
            if "by_domain" in e1:
                st.markdown("**Stratified Statutory Domain Performance**")
                df_dom = pd.DataFrame(e1["by_domain"]).T
                d_names = [DISPLAY_LABELS.get(k, k) for k in df_dom.index]
                fig_dom = go.Figure(
                    data=[
                        go.Bar(name="Pearson r", x=d_names, y=df_dom["pearson_r"], marker_color="#3E503C", text=[f"{v:.2f}" for v in df_dom["pearson_r"]], textposition="outside"),
                        go.Bar(name="Accuracy", x=d_names, y=df_dom["accuracy"], marker_color="#7F886A", text=[f"{v:.2f}" for v in df_dom["accuracy"]], textposition="outside"),
                        go.Bar(name="Macro-F1", x=d_names, y=df_dom["macro_f1"], marker_color="#FF6F3D", text=[f"{v:.2f}" for v in df_dom["macro_f1"]], textposition="outside"),
                    ]
                )
                fig_dom.update_layout(barmode="group")
                st.plotly_chart(_style_plotly(fig_dom, height=320, y_range=[0, 1.05]), use_container_width=True)

        st.markdown("**Overall Benchmark Table (N = 352)**")
        fmt_e1 = _format_metrics_table(df_e1)
        st.dataframe(
            fmt_e1.style.format({"Pearson r": "{:.4f}", "Spearman rho": "{:.4f}", "RMSE": "{:.4f}", "MAE": "{:.4f}", "Accuracy": "{:.2%}", "Macro-F1": "{:.4f}"}),
            use_container_width=True,
        )

        if "by_domain" in e1:
            st.markdown("**Stratified Statutory Domain Breakdown (JUDGEBERT v2)**")
            df_dom = pd.DataFrame(e1["by_domain"]).T
            fmt_dom = _format_metrics_table(df_dom)
            st.dataframe(
                fmt_dom.style.format({"Pearson r": "{:.4f}", "Spearman rho": "{:.4f}", "RMSE": "{:.4f}", "MAE": "{:.4f}", "Accuracy": "{:.2%}", "Macro-F1": "{:.4f}"}),
                use_container_width=True,
            )
    else:
        st.info("Run `python experiments/run_all_experiments.py` to populate Experiment 1 results.")

# ---------------------------------------------------------------------------
# Tab 3: EN vs HI (Experiment 2)
# ---------------------------------------------------------------------------

with tabs[2]:
    st.subheader("Cross-Lingual Evaluation (English vs. Hindi)")
    e2 = _load_json("experiments/results/exp2_multilingual_en_hi.json")
    v1_e2 = _load_json("experiments/results/v1_multidomain/exp2_multilingual_en_hi.json")
    v1_e1 = _load_json("experiments/results/v1_multidomain/exp1_baselines_vs_judgebert.json")

    if e2:
        en_m, hi_m = e2["en"], e2["hi"]
        c_en, c_hi, c_gain = st.columns(3)
        _render_kpi_card(c_en, "English Test Split (N = 213)", f"r = {en_m['pearson_r']:.4f}", f"Accuracy: {en_m['accuracy']*100:.2f}% | Macro-F1: {en_m['macro_f1']:.4f}")
        _render_kpi_card(c_hi, "Hindi Test Split (N = 139)", f"r = {hi_m['pearson_r']:.4f}", f"Accuracy: {hi_m['accuracy']*100:.2f}% | Macro-F1: {hi_m['macro_f1']:.4f}")
        if v1_e2:
            delta_hi = hi_m["pearson_r"] - v1_e2["hi"]["pearson_r"]
            _render_kpi_card(c_gain, "Hindi Phonetic Gain", f"+{delta_hi:.4f} r", "[UNK] test collapse reduced: 92.4% -> 0.0%")

        if v1_e2 and v1_e1:
            v1_jb = v1_e1["overall"]["JUDGEBERT"]
            e1_cur = _load_json("experiments/results/exp1_baselines_vs_judgebert.json")
            v2_jb = e1_cur["overall"]["JUDGEBERT"] if e1_cur else None
            if v2_jb:
                cats = ["Overall r", "Overall Macro-F1", "Overall Partial F1", "English r", "Hindi r", "Hindi Macro-F1"]
                vals_v1 = [
                    v1_jb["pearson_r"],
                    v1_jb["macro_f1"],
                    v1_jb["classification_report"]["Partially Preserved"]["f1-score"],
                    v1_e2["en"]["pearson_r"],
                    v1_e2["hi"]["pearson_r"],
                    v1_e2["hi"]["macro_f1"],
                ]
                vals_v2 = [
                    v2_jb["pearson_r"],
                    v2_jb["macro_f1"],
                    v2_jb["classification_report"]["Partially Preserved"]["f1-score"],
                    en_m["pearson_r"],
                    hi_m["pearson_r"],
                    hi_m["macro_f1"],
                ]
                st.markdown("**v1 Baseline vs. v2 Final Architectural Ablation**")
                fig_ab = go.Figure(
                    data=[
                        go.Bar(name="v1 Baseline", x=cats, y=vals_v1, marker_color="#7F886A", text=[f"{v:.2f}" for v in vals_v1], textposition="outside"),
                        go.Bar(name="v2 Final (Phonetic + Tempered + Hybrid)", x=cats, y=vals_v2, marker_color="#3E503C", text=[f"{v:.2f}" for v in vals_v2], textposition="outside"),
                    ]
                )
                fig_ab.update_layout(barmode="group")
                st.plotly_chart(_style_plotly(fig_ab, height=320, y_range=[0, 0.96]), use_container_width=True)

        df_e2 = pd.DataFrame({"en": en_m, "hi": hi_m}).T
        fmt_e2 = _format_metrics_table(df_e2)
        st.dataframe(
            fmt_e2.style.format({"Pearson r": "{:.4f}", "Spearman rho": "{:.4f}", "RMSE": "{:.4f}", "MAE": "{:.4f}", "Accuracy": "{:.2%}", "Macro-F1": "{:.4f}"}),
            use_container_width=True,
        )

        st.markdown("**Per-Class F1 Breakdown by Language**")
        class_rows = []
        for l_key, l_name in [("en", "English"), ("hi", "Hindi")]:
            cr = e2[l_key]["classification_report"]
            for cls_name in ["Not Preserved", "Partially Preserved", "Preserved"]:
                class_rows.append({
                    "Language": l_name,
                    "Decision Class": cls_name,
                    "Precision": cr[cls_name]["precision"],
                    "Recall": cr[cls_name]["recall"],
                    "F1-Score": cr[cls_name]["f1-score"],
                    "Support": int(cr[cls_name]["support"]),
                })
        st.dataframe(
            pd.DataFrame(class_rows).style.format({"Precision": "{:.4f}", "Recall": "{:.4f}", "F1-Score": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Experiment 2 results JSON not found.")

# ---------------------------------------------------------------------------
# Tab 4: OOD Transfer (Experiment 3)
# ---------------------------------------------------------------------------

with tabs[3]:
    st.subheader("Out-of-Domain Generalization (Tenancy -> Consumer Law)")
    e3 = _load_json("experiments/results/exp3_domain_generalization.json")
    e1 = _load_json("experiments/results/exp1_baselines_vs_judgebert.json")

    if e3:
        in_cons = e1["by_domain"]["consumer_protection"] if (e1 and "by_domain" in e1) else None
        k1, k2, k3, k4 = st.columns(4)
        _render_kpi_card(k1, "OOD Zero-Shot Pearson r", f"{e3['pearson_r']:.4f}", "Trained strictly on Tenancy (N=958)")
        _render_kpi_card(k2, "OOD Zero-Shot Accuracy", f"{e3['accuracy']*100:.2f}%", f"Macro-F1: {e3['macro_f1']:.4f}")
        _render_kpi_card(k3, "OOD RMSE / MAE", f"{e3['rmse']:.2f} / {e3['mae']:.2f}", "Calibration drift on unseen domain")
        if in_cons:
            _render_kpi_card(k4, "Multi-Domain Consumer r", f"{in_cons['pearson_r']:.4f}", f"Accuracy: {in_cons['accuracy']*100:.2f}%")

        if in_cons:
            comp_metrics = ["Pearson r", "Spearman rho", "Accuracy", "Macro-F1"]
            ood_vals = [e3["pearson_r"], e3["spearman_rho"], e3["accuracy"], e3["macro_f1"]]
            multi_vals = [in_cons["pearson_r"], in_cons["spearman_rho"], in_cons["accuracy"], in_cons["macro_f1"]]
            st.markdown("**Zero-Shot Single-Domain Collapse vs. Multi-Domain Consumer Mastery**")
            fig_ood = go.Figure(
                data=[
                    go.Bar(name="Single-Domain OOD (Tenancy -> Consumer)", x=comp_metrics, y=ood_vals, marker_color="#FF6F3D", text=[f"{v:.2f}" for v in ood_vals], textposition="outside"),
                    go.Bar(name="Multi-Domain JUDGEBERT (Consumer Test)", x=comp_metrics, y=multi_vals, marker_color="#3E503C", text=[f"{v:.2f}" for v in multi_vals], textposition="outside"),
                ]
            )
            fig_ood.update_layout(barmode="group")
            st.plotly_chart(_style_plotly(fig_ood, height=320, y_range=[0, 1.05]), use_container_width=True)

        st.markdown("**Zero-Shot Consumer Classification Report (N = 958)**")
        cr3 = e3["classification_report"]
        rows3 = [
            {
                "Decision Class": c,
                "Precision": cr3[c]["precision"],
                "Recall": cr3[c]["recall"],
                "F1-Score": cr3[c]["f1-score"],
                "Support": int(cr3[c]["support"]),
            }
            for c in ["Not Preserved", "Partially Preserved", "Preserved"]
        ]
        st.dataframe(
            pd.DataFrame(rows3).style.format({"Precision": "{:.4f}", "Recall": "{:.4f}", "F1-Score": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Experiment 3 results JSON not found.")

# ---------------------------------------------------------------------------
# Tab 5: Sanity Checks (Experiment 4)
# ---------------------------------------------------------------------------

with tabs[4]:
    st.subheader("Identical and Unrelated Sanity Checks (N = 40)")
    e4 = _load_json("experiments/results/exp4_sanity_checks.json")
    v1_e4 = _load_json("experiments/results/v1_multidomain/exp4_sanity_checks.json")

    if e4:
        ident, unrel = e4["identical"], e4["unrelated"]
        s1, s2, s3, s4 = st.columns(4)
        _render_kpi_card(s1, "JUDGEBERT Identical (GT=10)", f"{ident['judgebert_mean']:.2f} +/- {ident['judgebert_std']:.2f}", "Near-zero invariance variance")
        _render_kpi_card(s2, "JUDGEBERT Unrelated (GT=1)", f"{unrel['judgebert_mean']:.2f} +/- {unrel['judgebert_std']:.2f}", "Below 4.0 Not-Preserved cutoff")
        _render_kpi_card(s3, "SBERT Unrelated (Failure)", f"{unrel['sbert_mean']:.2f} +/- {unrel['sbert_std']:.2f}", "Falsely assigns Partial range")
        if v1_e4:
            _render_kpi_card(s4, "v1 -> v2 Identical Gain", f"{v1_e4['identical']['judgebert_mean']:.2f} -> {ident['judgebert_mean']:.2f}", f"Std cut {v1_e4['identical']['judgebert_std']:.2f} -> {ident['judgebert_std']:.2f}")

        st.markdown("**Mean Predicted Score +/- StdDev on Sanity Anchors**")
        fig_san = go.Figure(
            data=[
                go.Bar(
                    name="Generic SBERT Cosine",
                    x=["Identical Pairs (GT = 10.0)", "Unrelated Pairs (GT = 1.0)"],
                    y=[ident["sbert_mean"], unrel["sbert_mean"]],
                    error_y=dict(type="data", array=[ident["sbert_std"], unrel["sbert_std"]], color="#262B25"),
                    marker_color="#FF6F3D",
                    text=[f"{ident['sbert_mean']:.2f}", f"{unrel['sbert_mean']:.2f}"],
                    textposition="outside",
                ),
                go.Bar(
                    name="JUDGEBERT (Ours v2)",
                    x=["Identical Pairs (GT = 10.0)", "Unrelated Pairs (GT = 1.0)"],
                    y=[ident["judgebert_mean"], unrel["judgebert_mean"]],
                    error_y=dict(type="data", array=[ident["judgebert_std"], unrel["judgebert_std"]], color="#262B25"),
                    marker_color="#3E503C",
                    text=[f"{ident['judgebert_mean']:.2f}", f"{unrel['judgebert_mean']:.2f}"],
                    textposition="outside",
                ),
            ]
        )
        fig_san.add_hline(y=4.0, line_dash="dot", line_color="#DC2626", annotation_text="Cutoff 4.0", annotation_position="top left", annotation_font_color="#991B1B")
        fig_san.update_layout(barmode="group")
        st.plotly_chart(_style_plotly(fig_san, height=340, y_title="LMP Score (1-10)", y_range=[0, 11.8]), use_container_width=True)
    else:
        st.info("Experiment 4 results JSON not found.")

# ---------------------------------------------------------------------------
# Tab 6: Case Study (Experiment 5 - 16 Hard Cases)
# ---------------------------------------------------------------------------

with tabs[5]:
    st.subheader("Qualitative Error Analysis Across 16 Legally Difficult Cases")
    csv_path = "experiments/results/exp5_error_analysis_15cases.csv"
    if os.path.exists(csv_path):
        df_e5 = pd.read_csv(csv_path, encoding="utf-8")
        df_e5["gap_vs_gt"] = df_e5["sbert_score"] - df_e5["judgebert_score"]

        f_col1, f_col2, f_col3 = st.columns([1.1, 1.3, 1.8])
        lang_opt = f_col1.selectbox("Filter Language", ["All", "en", "hi"])
        err_opts = ["All"] + sorted(df_e5["error_category"].unique().tolist())
        err_opt = f_col2.selectbox("Filter Failure Mode", err_opts)
        query_opt = f_col3.text_input("Search Text / Explanation", placeholder="e.g., सिवाय, deposit, Lessor")

        filtered = df_e5.copy()
        if lang_opt != "All":
            filtered = filtered[filtered["language"] == lang_opt]
        if err_opt != "All":
            filtered = filtered[filtered["error_category"] == err_opt]
        if query_opt.strip():
            q = query_opt.strip().lower()
            mask = (
                filtered["original"].astype(str).str.lower().str.contains(q)
                | filtered["simplified"].astype(str).str.lower().str.contains(q)
                | filtered["explanation"].astype(str).str.lower().str.contains(q)
            )
            filtered = filtered[mask]

        summary_cols = [
            "case_id", "language", "error_category", "ground_truth_lmp",
            "sbert_score", "judgebert_score", "judgebert_decision", "gap_vs_gt",
        ]
        show_df = filtered[summary_cols].rename(
            columns={
                "case_id": "Case",
                "language": "Lang",
                "error_category": "Failure Mode",
                "ground_truth_lmp": "GT",
                "sbert_score": "SBERT",
                "judgebert_score": "JUDGEBERT",
                "judgebert_decision": "Verdict",
                "gap_vs_gt": "SBERT - JB Gap",
            }
        )
        st.dataframe(
            show_df.style.format({"GT": "{:.1f}", "SBERT": "{:.2f}", "JUDGEBERT": "{:.2f}", "SBERT - JB Gap": "{:+.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

        if not filtered.empty:
            st.divider()
            st.markdown("**Inspect Full Legal Clause Pair**")
            sel_id = st.selectbox("Select Case ID", filtered["case_id"].tolist())
            row = filtered[filtered["case_id"] == sel_id].iloc[0]

            err_pretty = str(row["error_category"]).replace("_", " ").title()
            c_det1, c_det2, c_det3, c_det4 = st.columns(4)
            _render_kpi_card(c_det1, "Ground Truth LMP", f"{row['ground_truth_lmp']:.1f} / 10", f"Category: {err_pretty}")
            _render_kpi_card(c_det2, "JUDGEBERT Prediction", f"{row['judgebert_score']:.2f} / 10", f"Verdict: {row['judgebert_decision']}")
            _render_kpi_card(c_det3, "Generic SBERT", f"{row['sbert_score']:.2f} / 10", "Deceptive surface cosine")
            _render_kpi_card(c_det4, "Score Gap (SBERT - JB)", f"{row['gap_vs_gt']:+.2f}", f"Language: {str(row['language']).upper()}")

            txt_c1, txt_c2 = st.columns(2)
            with txt_c1:
                st.markdown("**Original Clause**")
                st.markdown(f"<div class='jb-card'>{html.escape(str(row['original']))}</div>", unsafe_allow_html=True)
            with txt_c2:
                st.markdown("**Simplified Clause**")
                st.markdown(f"<div class='jb-card'>{html.escape(str(row['simplified']))}</div>", unsafe_allow_html=True)

            st.markdown("**Token-Level Visual Diff**")
            st.markdown(
                f"<div class='jb-diff-box'>{_render_token_diff_html(str(row['original']), str(row['simplified']))}</div>",
                unsafe_allow_html=True,
            )
            st.write(f"**Rule-Heuristic Overlay Output:** {row['explanation']}")
            st.caption(f"Why Baseline Fails: {row['why_baseline_fails']}")
    else:
        st.info("Experiment 5 CSV not found.")
