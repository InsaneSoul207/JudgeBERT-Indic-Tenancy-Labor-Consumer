"""
Generates publication-grade IEEE two-column Word (.docx), PDF (.pdf), and
Matplotlib figures from paper/IEEE_Research_Paper.md.
"""

from __future__ import annotations

import base64
import html
from html.parser import HTMLParser
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT_DIR = Path(__file__).resolve().parent.parent
PAPER_DIR = Path(__file__).resolve().parent
FIG_DIR = PAPER_DIR / "figures"
MD_PATH = PAPER_DIR / "IEEE_Research_Paper.md"
DOCX_PATH = PAPER_DIR / "IEEE_Research_Paper.docx"
PDF_PATH = PAPER_DIR / "IEEE_Research_Paper.pdf"


# ---------------------------------------------------------------------------
# 1. Generate Crisp High-DPI Academic Figures
# ---------------------------------------------------------------------------

def generate_all_figures() -> None:
    """Create publication-quality PNG figures (300 DPI) for the IEEE paper."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "axes.edgecolor": "#334155",
        "axes.linewidth": 0.8,
        "xtick.color": "#1e293b",
        "ytick.color": "#1e293b",
        "text.color": "#0f172a",
    })
    _draw_architecture_diagram(FIG_DIR / "fig1_architecture.png")
    _draw_exp1_baselines_domains(FIG_DIR / "fig2_exp1_baselines_domains.png")
    _draw_v1_v2_ablation(FIG_DIR / "fig3_v1_v2_multilingual_ablation.png")
    _draw_ood_and_sanity(FIG_DIR / "fig4_ood_sanity_cases.png")


def _box(ax, x, y, w, h, text, fc="#f8fafc", ec="#1e3a8a", tc="#0f172a", fs=8.3, bold=False, lw=1.2):
    patch = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h / 2, text,
        ha="center", va="center",
        fontsize=fs, fontweight="bold" if bold else "normal",
        color=tc, linespacing=1.22,
    )


def _arrow(ax, x1, y1, x2, y2, color="#334155"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, shrinkA=1, shrinkB=1),
    )


def _draw_architecture_diagram(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 4.35), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.35)
    ax.axis("off")

    # Top row: Neural Cross-Encoder Pipeline
    _box(ax, 0.15, 2.55, 1.85, 1.45,
         "Legal Clause Pair\n(S_orig, S_simp)\n\nEN & HI Devanagari\n3 Indian Statutory\nDomains (N=2,695)",
         fc="#eff6ff", ec="#1d4ed8", fs=8.0, bold=True)

    _arrow(ax, 2.02, 3.28, 2.30, 3.28)
    _box(ax, 2.32, 2.55, 2.05, 1.45,
         "Phonetic Transducer\n& Tokenization\n\nDevanagari -> Latin\n[UNK]: 92.4% -> 0.0%\n[CLS] S1 [SEP] S2 [SEP]\nmax_len = 256",
         fc="#ecfdf5", ec="#047857", fs=7.8)

    _arrow(ax, 4.39, 3.28, 4.67, 3.28)
    _box(ax, 4.69, 2.55, 2.15, 1.45,
         "MiniLM-L6-v2 Backbone\nCross-Attention\n\n6 Layers, 12 Heads, 384d\nAll 22.87M Params Unfrozen\nh_pool = 0.5 CLS + 0.5 Mean\nDense(384) + GELU + Drop(0.2)",
         fc="#f8fafc", ec="#334155", fs=7.6)

    # Branch to 3 Heads
    _arrow(ax, 6.86, 3.72, 7.28, 3.82)
    _arrow(ax, 6.86, 3.28, 7.28, 3.12)
    _arrow(ax, 6.86, 2.82, 7.28, 2.42)

    _box(ax, 7.30, 3.55, 3.00, 0.56,
         "Regression Head (385p): 1 + 9*sigma(w^T z)\n-> Continuous LMP Score [1.0, 10.0]",
         fc="#fefce8", ec="#a16207", fs=7.6, bold=True)
    _box(ax, 7.30, 2.84, 3.00, 0.56,
         "Decision Head (1,155p) + Calibration Gate\n-> Preserved / Partial / Not Preserved",
         fc="#fef2f2", ec="#b91c1c", fs=7.6, bold=True)
    _box(ax, 7.30, 2.13, 3.00, 0.56,
         "Error Taxonomy Head (3,850p): Softmax(W_e z)\n-> 10 Classes (None + 9 Legal Breaches)",
         fc="#f3e8ff", ec="#6d28d9", fs=7.6, bold=True)

    # Bottom track: Training Loss + Neuro-Symbolic Diagnostics
    _box(ax, 0.15, 0.35, 5.15, 1.45,
         "Composite Multi-Task Objective (GPU Fine-Tuning, Batch=16, AdamW lr=3.5e-5, 12 Epochs)\n"
         "L_total = w_lang * [ L_Huber + 0.85 * L_CE^dec + 0.50 * L_CE^err + 0.35 * L_cons ]\n"
         "- Hindi gradient multiplier w_lang = 1.5x | Tempered class weights (N / (K * N_c))^0.65\n"
         "- Dual-head consistency L_cons aligns sigmoid score with 3-way ordinal probabilities\n"
         "- Train-only contrastive & numeric anchors (2,013 -> 2,385 pairs; Best Val Checkpoint: Epoch 11)",
         fc="#f8fafc", ec="#475569", fs=7.6)

    _box(ax, 5.55, 0.35, 4.75, 1.45,
         "Bilingual Rule-Guided Explainability & Dashboard Overlay\n"
         "analyze_legal_discrepancy(S_orig, S_simp, lang, score, err_type)\n"
         "- Regex numeric, currency & limitation deadline extraction (EN + HI digits)\n"
         "- Deontic modals ('shall'->'may', 'anivarya'->'chaahe to') & negation polarity\n"
         "- Exceptions ('unless'/'sivaay') & party swaps -> 6-Tab Streamlit UI",
         fc="#f0f9ff", ec="#0369a1", fs=7.6)

    _arrow(ax, 5.75, 2.53, 3.80, 1.82, color="#64748b")
    _arrow(ax, 1.10, 2.53, 6.20, 1.82, color="#0369a1")
    _arrow(ax, 8.80, 2.11, 8.80, 1.82, color="#0369a1")

    fig.tight_layout(pad=0.25)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _draw_exp1_baselines_domains(out_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 3.15), dpi=300)

    # Panel A: Baselines vs JUDGEBERT
    models = ["BLEU", "ROUGE-L", "Leven.", "TF-IDF", "SBERT", "JB-v1", "JB-v2\n(Ours)"]
    pearson = [0.1163, 0.1528, 0.0987, 0.2047, 0.2850, 0.5843, 0.7436]
    macro_f1 = [0.3792, 0.3591, 0.3465, 0.4044, 0.2978, 0.4876, 0.7367]
    x = np.arange(len(models))
    w = 0.36
    b1 = ax1.bar(x - w / 2, pearson, w, label="Pearson r", color="#1e3a8a", edgecolor="#0f172a", linewidth=0.5)
    b2 = ax1.bar(x + w / 2, macro_f1, w, label="Macro-F1", color="#0d9488", edgecolor="#0f172a", linewidth=0.5)
    for rect in list(b1) + list(b2):
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2, h + 0.015, f"{h:.2f}", ha="center", va="bottom", fontsize=7.0)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=8.0)
    ax1.set_ylim(0, 0.92)
    ax1.set_ylabel("Score (0 - 1 Scale)", fontsize=8.5)
    ax1.set_title("(a) Baselines vs. JUDGEBERT (Test N=352)", fontsize=9.2, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.legend(fontsize=7.8, loc="upper left", frameon=True)

    # Panel B: Domains
    domains = ["Consumer Law\n(N=125)", "Tenancy Law\n(N=133)", "Labor & Contracts\n(N=94)"]
    d_r = [0.8673, 0.7284, 0.6153]
    d_acc = [0.8800, 0.7594, 0.7128]
    d_pf1 = [0.6857, 0.5306, 0.3478]
    x2 = np.arange(len(domains))
    w2 = 0.25
    c1 = ax2.bar(x2 - w2, d_r, w2, label="Pearson r", color="#1d4ed8", edgecolor="#0f172a", linewidth=0.5)
    c2 = ax2.bar(x2, d_acc, w2, label="Accuracy", color="#059669", edgecolor="#0f172a", linewidth=0.5)
    c3 = ax2.bar(x2 + w2, d_pf1, w2, label="Partial F1", color="#d97706", edgecolor="#0f172a", linewidth=0.5)
    for rect in list(c1) + list(c2) + list(c3):
        h = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width() / 2, h + 0.015, f"{h:.2f}", ha="center", va="bottom", fontsize=7.0)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(domains, fontsize=8.0)
    ax2.set_ylim(0, 1.02)
    ax2.set_title("(b) Stratified Performance Across Legal Domains", fontsize=9.2, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.legend(fontsize=7.6, loc="upper right", frameon=True)

    fig.tight_layout(pad=1.0)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _draw_v1_v2_ablation(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 2.75), dpi=300)
    categories = [
        "Overall Pearson r", "Overall Macro-F1", "Overall Partial F1",
        "English Pearson r", "Hindi Pearson r", "Hindi Macro-F1",
    ]
    v1_vals = [0.5843, 0.4876, 0.0000, 0.7015, 0.3910, 0.4310]
    v2_vals = [0.7436, 0.7367, 0.5421, 0.7901, 0.6817, 0.7037]
    x = np.arange(len(categories))
    w = 0.35
    b1 = ax.bar(x - w / 2, v1_vals, w, label="JUDGEBERT v1 (Baseline)", color="#94a3b8", edgecolor="#334155", linewidth=0.6)
    b2 = ax.bar(x + w / 2, v2_vals, w, label="JUDGEBERT v2 (Phonetic + Tempered + Hybrid Pool)", color="#1e40af", edgecolor="#0f172a", linewidth=0.6)
    for r1, r2 in zip(b1, b2):
        h1, h2 = r1.get_height(), r2.get_height()
        ax.text(r1.get_x() + r1.get_width() / 2, h1 + 0.015, f"{h1:.2f}", ha="center", va="bottom", fontsize=7.3, color="#475569")
        ax.text(r2.get_x() + r2.get_width() / 2, h2 + 0.015, f"{h2:.2f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#1e3a8a")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=8.0, rotation=10, ha="right")
    ax.set_ylim(0, 1.04)
    ax.set_ylabel("Metric Value (0 - 1)", fontsize=8.5)
    ax.set_title("Architectural Ablation: v1 Baseline vs. v2 Final (Hindi +0.291 r, Partial F1 0.00 -> 0.54)", fontsize=9.2, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=7.8, loc="upper right", ncol=2, frameon=True)
    fig.tight_layout(pad=0.8)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _draw_ood_and_sanity(out_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 2.95), dpi=300)

    # Panel A: Exp 3 OOD
    metrics = ["Pearson r", "Spearman rho", "Accuracy", "Macro-F1"]
    ood = [0.2149, 0.1579, 0.3528, 0.3503]
    multi = [0.8673, 0.8697, 0.8800, 0.8358]
    x = np.arange(len(metrics))
    w = 0.34
    b1 = ax1.bar(x - w / 2, ood, w, label="Single-Domain OOD (Tenancy -> Consumer)", color="#dc2626", alpha=0.85, edgecolor="#7f1d1d", linewidth=0.5)
    b2 = ax1.bar(x + w / 2, multi, w, label="Multi-Domain JUDGEBERT (Consumer Test)", color="#15803d", edgecolor="#14532d", linewidth=0.5)
    for rect in list(b1) + list(b2):
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width() / 2, h + 0.015, f"{h:.2f}", ha="center", va="bottom", fontsize=7.3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=8.2)
    ax1.set_ylim(0, 1.03)
    ax1.set_title("(a) Exp 3: Zero-Shot OOD Collapse vs. Multi-Domain", fontsize=9.0, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.legend(fontsize=7.3, loc="upper left", frameon=True)

    # Panel B: Exp 4 Sanity Checks
    labels = ["Identical Pairs\n(GT = 10.0)", "Unrelated Pairs\n(GT = 1.0)"]
    sbert_means = [10.00, 5.62]
    sbert_stds = [0.00, 2.46]
    jb_means = [9.63, 2.99]
    jb_stds = [0.02, 2.56]
    x2 = np.arange(len(labels))
    s1 = ax2.bar(x2 - w / 2, sbert_means, w, yerr=sbert_stds, capsize=4, label="Generic SBERT Cosine", color="#f59e0b", edgecolor="#78350f", linewidth=0.5)
    s2 = ax2.bar(x2 + w / 2, jb_means, w, yerr=jb_stds, capsize=4, label="JUDGEBERT v2 (Ours)", color="#1d4ed8", edgecolor="#1e3a8a", linewidth=0.5)
    ax2.axhline(4.0, color="#64748b", linestyle=":", linewidth=1.0, label="Not-Preserved Cutoff (4.0)")
    for rect, err in zip(list(s1) + list(s2), sbert_stds + jb_stds):
        h = rect.get_height()
        y_pos = h + err + 0.25 if err > 0.2 else h + 0.25
        ax2.text(rect.get_x() + rect.get_width() / 2, min(y_pos, 10.7), f"{h:.2f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(labels, fontsize=8.2)
    ax2.set_ylim(0, 12.8)
    ax2.set_ylabel("Predicted LMP Score (1 - 10)", fontsize=8.3)
    ax2.set_title("(b) Exp 4: Identical vs. Unrelated Sanity Bounds", fontsize=9.0, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.legend(fontsize=7.3, loc="upper right", frameon=True)

    fig.tight_layout(pad=1.0)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Inline Math & Markdown Formatter (Zero Raw $ or LaTeX Leaks)
# ---------------------------------------------------------------------------

LATEX_MAP = {
    r"\hat{y}_{\text{LMP}}": "<i>&#375;</i><sub>LMP</sub>",
    r"\hat{y}_{\text{dec}}": "<i>&#375;</i><sub>dec</sub>",
    r"\hat{y}_{\text{err}}": "<i>&#375;</i><sub>err</sub>",
    r"y_{\text{LMP}}": "<i>y</i><sub>LMP</sub>",
    r"\mathbf{h}_{\text{pool}}": "<b>h</b><sub>pool</sub>",
    r"\mathbf{h}_{[\text{CLS}]}": "<b>h</b><sub>[CLS]</sub>",
    r"\mathbf{h}_{\text{mean}}": "<b>h</b><sub>mean</sub>",
    r"\mathbf{h}_t": "<b>h</b><sub><i>t</i></sub>",
    r"\mathbf{w}_{\text{reg}}^T": "<b>w</b><sub>reg</sub><sup>T</sup>",
    r"\mathbf{z}": "<b>z</b>",
    r"\mathcal{L}_{\text{total}}": "&#8466;<sub>total</sub>",
    r"\mathcal{L}_{\text{Huber}}": "&#8466;<sub>Huber</sub>",
    r"\mathcal{L}_{\text{CE}}^{\text{dec}}": "&#8466;<sub>CE</sub><sup>dec</sup>",
    r"\mathcal{L}_{\text{CE}}^{\text{err}}": "&#8466;<sub>CE</sub><sup>err</sup>",
    r"\mathcal{L}_{\text{cons}}": "&#8466;<sub>cons</sub>",
    r"\mathbb{I}_{\text{hi}}": "&#120128;<sub>hi</sub>",
    r"\mathbb{E}": "&#120124;",
    r"\mathcal{Y}": "&#119988;",
    r"\mathcal{E}": "&#8496;",
    r"\text{MSE}": "MSE",
    r"\text{weight\_decay}": "weight\uE002decay",
    r"\rightarrow": "&rarr;",
    r"\to": "&rarr;",
    r"\leftrightarrow": "&harr;",
    r"\uparrow": "&uarr;",
    r"\downarrow": "&darr;",
    r"\approx": "&asymp;",
    r"\times": "&times;",
    r"\cdot": "&middot;",
    r"\pm": "&plusmn;",
    r"\in": "&isin;",
    r"\propto": "&prop;",
    r"\sigma": "&sigma;",
    r"\rho": "&rho;",
    r"\,": " ",
    r"\;": " ",
    r"\!": "",
    r"\_": "\uE002",
}


def _convert_latex_expr(expr: str) -> str:
    s = expr.strip()
    s = re.sub(
        r"\\frac\{\\sum_\{t=1\}\^\{L\}\s*m_t\s*\\mathbf\{h\}_t\}\{\\sum_\{t=1\}\^\{L\}\s*m_t\}",
        "( &Sigma;<sub><i>t</i>=1..<i>L</i></sub> <i>m<sub>t</sub></i><b>h</b><sub><i>t</i></sub> ) / ( &Sigma;<sub><i>t</i>=1..<i>L</i></sub> <i>m<sub>t</sub></i> )",
        s,
    )
    s = re.sub(
        r"\\frac\{\\hat\{y\}_\{\\text\{LMP\}\}\s*-\s*1\.0\}\{9\.0\}",
        "(<i>&#375;</i><sub>LMP</sub> &minus; 1.0) / 9.0",
        s,
    )
    for k, v in LATEX_MAP.items():
        s = s.replace(k, v)
    s = re.sub(r"\\text\{([^}]*)\}", lambda m: m.group(1).replace("_", "\uE002"), s)
    s = s.replace(r"\left(", "(").replace(r"\right)", ")")
    s = s.replace(r"\left[", "[").replace(r"\right]", "]")
    s = s.replace(r"\left", "").replace(r"\right", "")
    # Subscripts and superscripts before cleaning braces
    s = re.sub(r"([A-Za-z0-9)])\^\{([^}]+)\}", r"\1<sup>\2</sup>", s)
    s = re.sub(r"([A-Za-z0-9)])\^([A-Za-z0-9.\-]+)", r"\1<sup>\2</sup>", s)
    s = re.sub(r"([A-Za-z0-9])_\{([^}]+)\}", r"<i>\1</i><sub>\2</sub>", s)
    s = re.sub(r"([A-Za-z0-9])_([A-Za-z0-9])", r"<i>\1</i><sub>\2</sub>", s)
    s = s.replace("{", "").replace("}", "").replace("\\", "").replace("\uE002", "_")
    return s


def _inline_to_html(text: str, allow_wbr: bool = True) -> str:
    tokens: list[str] = []

    def _stash_math(m):
        tokens.append(f"<span class='math'>{_convert_latex_expr(m.group(1))}</span>")
        return f"\uE000TOK{len(tokens) - 1}\uE001"

    def _stash_code(m):
        code_html = html.escape(m.group(1))
        if allow_wbr:
            code_html = code_html.replace("/", "/<wbr>").replace("_", "_<wbr>")
        tokens.append(f"<code>{code_html}</code>")
        return f"\uE000TOK{len(tokens) - 1}\uE001"

    masked = re.sub(r"\$\$?(.+?)\$\$?", _stash_math, text)
    masked = re.sub(r"`([^`]+)`", _stash_code, masked)

    masked = masked.replace(r"\*", "\uE003STAR\uE004")
    esc = html.escape(masked)
    esc = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc)
    esc = re.sub(r"\*([^*]+?)\*", r"<i>\1</i>", esc)
    esc = esc.replace("\uE003STAR\uE004", "*")
    if allow_wbr:
        esc = re.sub(r"(https?://\S+)", lambda m: m.group(1).replace("/", "/<wbr>"), esc)

    for idx, val in enumerate(tokens):
        esc = esc.replace(f"\uE000TOK{idx}\uE001", val)
    return esc


def _strip_markup_for_plain(html_str: str) -> str:
    """Convert internal formatted HTML back to lightweight tokens for python-docx."""
    return html_str


# ---------------------------------------------------------------------------
# 3. Markdown Structured Parser
# ---------------------------------------------------------------------------

def parse_markdown_paper(md_path: Path) -> dict:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc_data = {
        "title": "",
        "header_lines": [],
        "abstract": "",
        "keywords": "",
        "blocks": [],
    }

    i = 0
    # Parse header block before ## Abstract
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# "):
            doc_data["title"] = line[2:].strip()
        elif line == "---":
            i += 1
            break
        elif line:
            doc_data["header_lines"].append(line)
        i += 1

    # Parse Abstract & Index Terms
    while i < len(lines):
        line = lines[i].strip()
        if line == "## Abstract":
            i += 1
            abs_parts = []
            while i < len(lines) and not lines[i].strip().startswith("**Index Terms**"):
                if lines[i].strip():
                    abs_parts.append(lines[i].strip())
                i += 1
            doc_data["abstract"] = " ".join(abs_parts)
            continue
        if line.startswith("**Index Terms**"):
            doc_data["keywords"] = line.replace("**Index Terms**—", "").replace("**Index Terms**:", "").strip()
        if line == "---" and doc_data["abstract"]:
            i += 1
            break
        i += 1

    # Parse body sections
    in_references = False
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or line == "---":
            i += 1
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            in_references = title.lower() == "references"
            doc_data["blocks"].append({"type": "h1", "text": title})
            i += 1
            continue

        if line.startswith("### "):
            doc_data["blocks"].append({"type": "h2", "text": line[4:].strip()})
            i += 1
            continue

        if line.startswith("[FIGURE:") and line.endswith("]"):
            inner = line[8:-1]
            fname, caption = inner.split("|", 1) if "|" in inner else (inner, "")
            doc_data["blocks"].append({"type": "figure", "filename": fname.strip(), "caption": caption.strip()})
            i += 1
            continue

        if line.startswith("$$") and line.endswith("$$") and len(line) > 4:
            doc_data["blocks"].append({"type": "equation", "expr": line[2:-2].strip()})
            i += 1
            continue

        # Table Caption + Markdown Table
        if line.startswith("**TABLE ") and i + 2 < len(lines) and lines[i + 2].strip().startswith("|"):
            caption = line.strip("*").strip()
            i += 2  # skip blank line before table
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            rows = []
            for tl in tbl_lines:
                cols = [c.strip() for c in tl.split("|")[1:-1]]
                if cols and all(set(c) <= set(":- ") for c in cols):
                    continue
                rows.append(cols)
            doc_data["blocks"].append({"type": "table", "caption": caption, "rows": rows})
            continue

        # Standalone Markdown Table without explicit caption
        if line.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            rows = []
            for tl in tbl_lines:
                cols = [c.strip() for c in tl.split("|")[1:-1]]
                if cols and all(set(c) <= set(":- ") for c in cols):
                    continue
                rows.append(cols)
            doc_data["blocks"].append({"type": "table", "caption": "", "rows": rows})
            continue

        # Bullet / Numbered list
        if re.match(r"^(\- |\d+\.\s)", line):
            items = []
            ordered = bool(re.match(r"^\d+\.\s", line))
            while i < len(lines) and lines[i].strip():
                l = lines[i].strip()
                if not re.match(r"^(\- |\d+\.\s)", l):
                    break
                item_txt = re.sub(r"^(\- |\d+\.\s)", "", l)
                items.append(item_txt)
                i += 1
            doc_data["blocks"].append({"type": "list", "ordered": ordered, "items": items})
            continue

        # References block
        if in_references and re.match(r"^\[\d+\]", line):
            doc_data["blocks"].append({"type": "ref", "text": line})
            i += 1
            continue

        # Standard paragraph (merge wrapped continuation lines)
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt == "---"
                or nxt.startswith("#")
                or nxt.startswith("|")
                or nxt.startswith("[FIGURE:")
                or nxt.startswith("**TABLE ")
                or nxt.startswith("$$")
                or re.match(r"^(\- |\d+\.\s|\[\d+\])", nxt)
            ):
                break
            para_lines.append(nxt)
            i += 1
        doc_data["blocks"].append({"type": "para", "text": " ".join(para_lines)})

    return doc_data


# ---------------------------------------------------------------------------
# 4. Generate True IEEE Two-Column PDF via Chrome/Edge Headless
# ---------------------------------------------------------------------------

def _img_to_data_uri(img_path: Path) -> str:
    raw = img_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _build_ieee_html(doc_data: dict) -> str:
    title_html = html.escape(doc_data["title"])
    header_html_lines = [_inline_to_html(h) for h in doc_data["header_lines"]]
    abs_html = _inline_to_html(doc_data["abstract"])
    kw_html = _inline_to_html(doc_data["keywords"])

    fig_counter = 0
    body_parts = []
    for blk in doc_data["blocks"]:
        btype = blk["type"]
        if btype == "h1":
            txt = html.escape(blk["text"])
            # Format section header in IEEE uppercase small-caps centered style
            body_parts.append(f"<h2 class='ieee-h1'>{txt}</h2>")
        elif btype == "h2":
            body_parts.append(f"<h3 class='ieee-h2'>{_inline_to_html(blk['text'])}</h3>")
        elif btype == "para":
            cls = "ieee-note" if (blk["text"].startswith("*Note:") or blk["text"].startswith("*†")) else "ieee-p"
            body_parts.append(f"<p class='{cls}'>{_inline_to_html(blk['text'])}</p>")
        elif btype == "list":
            tag = "ol" if blk["ordered"] else "ul"
            li_html = "".join(f"<li>{_inline_to_html(item)}</li>" for item in blk["items"])
            body_parts.append(f"<{tag} class='ieee-list'>{li_html}</{tag}>")
        elif btype == "equation":
            eq_html = _convert_latex_expr(blk["expr"])
            body_parts.append(f"<div class='ieee-eq'>{eq_html}</div>")
        elif btype == "ref":
            body_parts.append(f"<p class='ieee-ref'>{_inline_to_html(blk['text'])}</p>")
        elif btype == "figure":
            fig_counter += 1
            fig_path = FIG_DIR / blk["filename"]
            uri = _img_to_data_uri(fig_path) if fig_path.exists() else ""
            cap = _inline_to_html(blk["caption"])
            body_parts.append(
                f"<div class='ieee-figure-wide'>"
                f"<img src='{uri}' alt='Fig. {fig_counter}' />"
                f"<div class='fig-cap'><b>Fig. {fig_counter}.</b> {cap}</div>"
                f"</div>"
            )
        elif btype == "table":
            rows = blk["rows"]
            if not rows:
                continue
            ncols = len(rows[0])
            wide_cls = "ieee-table-wrap-wide" if (ncols >= 5 or "TABLE IV:" in blk["caption"]) else "ieee-table-wrap-col"
            if wide_cls == "ieee-table-wrap-wide" and len(rows) > 12:
                wide_cls = "ieee-table-wrap-wide-split"
            cap_html = _inline_to_html(blk["caption"], allow_wbr=False)
            thead = "".join(f"<th>{_inline_to_html(c, allow_wbr=False)}</th>" for c in rows[0])
            tbody_rows = []
            for r in rows[1:]:
                tds = "".join(f"<td>{_inline_to_html(c)}</td>" for c in r)
                tbody_rows.append(f"<tr>{tds}</tr>")
            body_parts.append(
                f"<div class='{wide_cls}'>"
                f"<div class='tbl-cap'>{cap_html}</div>"
                f"<table class='ieee-tbl'><thead><tr>{thead}</tr></thead>"
                f"<tbody>{''.join(tbody_rows)}</tbody></table>"
                f"</div>"
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{title_html}</title>
<style>
  @page {{
    size: letter;
    margin: 0.56in 0.56in 0.58in 0.56in;
    @top-right {{
      content: "CSET 346 (PJ_08) | IEEE Project Report";
      font-family: "Times New Roman", serif;
      font-size: 7.5pt;
      color: #64748b;
    }}
    @bottom-center {{
      content: counter(page);
      font-family: "Times New Roman", serif;
      font-size: 8.5pt;
      color: #334155;
    }}
  }}
  @page :first {{
    @top-right {{ content: none; }}
  }}
  body {{
    font-family: "Times New Roman", "Nirmala UI", "Mangal", Times, serif;
    font-size: 9.15pt;
    line-height: 1.25;
    color: #0f172a;
    margin: 0;
    padding: 0;
  }}
  .top-banner {{
    text-align: center;
    margin-bottom: 10pt;
    border-bottom: 1.2pt solid #1e293b;
    padding-bottom: 8pt;
  }}
  .course-pill {{
    font-size: 8pt;
    color: #334155;
    letter-spacing: 0.4pt;
    text-transform: uppercase;
    margin-bottom: 4pt;
  }}
  h1.paper-title {{
    font-size: 19pt;
    line-height: 1.15;
    font-weight: 700;
    margin: 0 0 6pt 0;
    color: #0f172a;
  }}
  .author-line {{
    font-size: 9.5pt;
    margin: 2pt 0;
    color: #1e293b;
  }}
  .abstract-box {{
    text-align: justify;
    font-size: 8.8pt;
    line-height: 1.26;
    background: #f8fafc;
    border-left: 2.5pt solid #1e3a8a;
    padding: 6pt 8pt;
    margin: 8pt 0 6pt 0;
  }}
  .kw-line {{
    text-align: left;
    font-size: 8.5pt;
    margin: 0;
    color: #1e293b;
  }}
  .two-col {{
    column-count: 2;
    column-gap: 0.22in;
    column-fill: balance;
  }}
  h2.ieee-h1 {{
    font-size: 10.2pt;
    font-weight: 700;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.35pt;
    margin: 8pt 0 3.5pt 0;
    padding-bottom: 1.5pt;
    border-bottom: 0.6pt solid #cbd5e1;
    color: #0f172a;
    break-after: avoid;
  }}
  h3.ieee-h2 {{
    font-size: 9.5pt;
    font-weight: 700;
    font-style: italic;
    margin: 7pt 0 3pt 0;
    color: #1e293b;
    break-after: avoid;
  }}
  p.ieee-p {{
    text-align: justify;
    margin: 0 0 4.5pt 0;
    text-indent: 1.1em;
    hyphens: auto;
  }}
  p.ieee-note {{
    text-align: justify;
    font-size: 8.1pt;
    line-height: 1.22;
    color: #334155;
    margin: 3pt 0 6pt 0;
  }}
  .ieee-list {{
    margin: 2pt 0 5pt 0;
    padding-left: 14pt;
    text-align: justify;
  }}
  .ieee-list li {{
    margin-bottom: 2.5pt;
  }}
  .ieee-eq {{
    text-align: center;
    font-size: 9.3pt;
    margin: 5pt 0;
    padding: 3pt 4pt;
    background: #f8fafc;
    border-radius: 2pt;
    break-inside: avoid;
  }}
  code {{
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.1pt;
    color: #1e3a8a;
  }}
  .math {{
    font-style: normal;
  }}
  .ieee-figure-wide {{
    column-span: all;
    text-align: center;
    margin: 6pt 0 8pt 0;
    break-inside: avoid;
  }}
  .ieee-figure-wide img {{
    max-width: 100%;
    height: auto;
    border: 0.5pt solid #cbd5e1;
  }}
  .fig-cap {{
    font-size: 8.1pt;
    color: #1e293b;
    margin-top: 3pt;
    text-align: center;
  }}
  .ieee-table-wrap-wide {{
    column-span: all;
    margin: 6pt 0 7pt 0;
    break-inside: avoid;
  }}
  .ieee-table-wrap-wide-split {{
    column-span: all;
    margin: 6pt 0 7pt 0;
    break-inside: auto;
  }}
  .ieee-table-wrap-wide-split thead {{
    display: table-header-group;
  }}
  .ieee-table-wrap-wide-split tr {{
    break-inside: avoid;
  }}
  .ieee-table-wrap-col {{
    margin: 5pt 0 7pt 0;
    break-inside: avoid;
  }}
  .tbl-cap {{
    font-size: 8.2pt;
    font-weight: 700;
    text-align: center;
    margin-bottom: 3pt;
    color: #0f172a;
    break-after: avoid;
  }}
  table.ieee-tbl {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.7pt;
    line-height: 1.18;
    border-top: 1.3pt solid #0f172a;
    border-bottom: 1.3pt solid #0f172a;
    overflow-wrap: break-word;
    word-wrap: break-word;
  }}
  table.ieee-tbl th {{
    background: #f1f5f9;
    font-weight: 700;
    text-align: left;
    padding: 3pt 4pt;
    border-bottom: 0.8pt solid #475569;
  }}
  table.ieee-tbl td {{
    padding: 2.5pt 4pt;
    border-bottom: 0.35pt solid #e2e8f0;
    vertical-align: top;
  }}
  table.ieee-tbl tr:nth-child(even) td {{
    background: #fafafa;
  }}
  p.ieee-ref {{
    font-size: 8.1pt;
    line-height: 1.22;
    margin: 0 0 3pt 0;
    padding-left: 14pt;
    text-indent: -14pt;
    text-align: justify;
  }}
</style>
</head>
<body>
  <div class="top-banner">
    <div class="course-pill">Bennett University &bull; CSET 346 &ndash; Natural Language Processing &bull; Project Report (PJ_08)</div>
    <h1 class="paper-title">{title_html}</h1>
    {''.join(f"<div class='author-line'>{hl}</div>" for hl in header_html_lines)}
    <div class="abstract-box"><b><i>Abstract</i>&mdash;</b>{abs_html}</div>
    <div class="kw-line"><b><i>Index Terms</i>&mdash;</b>{kw_html}</div>
  </div>
  <div class="two-col">
    {''.join(body_parts)}
  </div>
</body>
</html>"""


def _find_headless_browser() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def generate_pdf(doc_data: dict) -> None:
    html_str = _build_ieee_html(doc_data)
    browser = _find_headless_browser()
    if browser:
        with tempfile.TemporaryDirectory() as tmpdir:
            html_file = Path(tmpdir) / "ieee_report.html"
            html_file.write_text(html_str, encoding="utf-8")
            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                f"--print-to-pdf={PDF_PATH}",
                "--no-pdf-header-footer",
                html_file.as_uri(),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if PDF_PATH.exists() and res.returncode == 0:
                print(f"Successfully generated IEEE two-column PDF via Chrome/Edge at {PDF_PATH}")
                return
            print("Warning: headless browser PDF print returned non-zero; falling back to ReportLab.", res.stderr)

    # Fallback ReportLab two-column generator if no Chromium browser installed
    _generate_pdf_reportlab_fallback(doc_data)


def _generate_pdf_reportlab_fallback(doc_data: dict) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import BaseDocTemplate, Frame, FrameBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, Image

    page_w, page_h = letter
    margin_x, margin_y = 42, 46
    gutter = 14
    col_w = (page_w - 2 * margin_x - gutter) / 2.0

    # Page 1: Top banner + 2 bottom columns; Subsequent pages: full-height 2 columns
    banner_h = 195
    f1_top = Frame(margin_x, page_h - margin_y - banner_h, page_w - 2 * margin_x, banner_h, id="banner")
    f1_left = Frame(margin_x, margin_y, col_w, page_h - 2 * margin_y - banner_h - 8, id="p1_left")
    f1_right = Frame(margin_x + col_w + gutter, margin_y, col_w, page_h - 2 * margin_y - banner_h - 8, id="p1_right")

    fn_left = Frame(margin_x, margin_y, col_w, page_h - 2 * margin_y, id="pn_left")
    fn_right = Frame(margin_x + col_w + gutter, margin_y, col_w, page_h - 2 * margin_y, id="pn_right")

    doc = BaseDocTemplate(str(PDF_PATH), pagesize=letter)
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[f1_top, f1_left, f1_right]),
        PageTemplate(id="Later", frames=[fn_left, fn_right]),
    ])

    s_title = ParagraphStyle("Title", fontName="Times-Bold", fontSize=16, leading=19, alignment=1, spaceAfter=4)
    s_meta = ParagraphStyle("Meta", fontName="Times-Roman", fontSize=8.5, leading=11, alignment=1, spaceAfter=3)
    s_abs = ParagraphStyle("Abs", fontName="Times-Roman", fontSize=8.2, leading=10.5, alignment=4, spaceAfter=4)
    s_h1 = ParagraphStyle("H1", fontName="Times-Bold", fontSize=10, leading=12, alignment=1, spaceBefore=8, spaceAfter=4)
    s_h2 = ParagraphStyle("H2", fontName="Times-BoldItalic", fontSize=9.2, leading=11.5, spaceBefore=6, spaceAfter=3)
    s_body = ParagraphStyle("Body", fontName="Times-Roman", fontSize=8.8, leading=11.2, alignment=4, spaceAfter=4)

    story = [Paragraph(html.escape(doc_data["title"]), s_title)]
    for hl in doc_data["header_lines"]:
        story.append(Paragraph(_inline_to_html(hl), s_meta))
    story.append(Paragraph(f"<b><i>Abstract</i>&mdash;</b>{_inline_to_html(doc_data['abstract'])}", s_abs))
    story.append(Paragraph(f"<b><i>Index Terms</i>&mdash;</b>{_inline_to_html(doc_data['keywords'])}", s_abs))
    story.append(FrameBreak())

    for blk in doc_data["blocks"]:
        if blk["type"] == "h1":
            story.append(Paragraph(html.escape(blk["text"].upper()), s_h1))
        elif blk["type"] == "h2":
            story.append(Paragraph(_inline_to_html(blk["text"]), s_h2))
        elif blk["type"] in ("para", "ref"):
            story.append(Paragraph(_inline_to_html(blk["text"]), s_body))
        elif blk["type"] == "equation":
            story.append(Paragraph(_convert_latex_expr(blk["expr"]), s_meta))
        elif blk["type"] == "list":
            for idx, item in enumerate(blk["items"], 1):
                prefix = f"{idx}. " if blk["ordered"] else "&bull; "
                story.append(Paragraph(prefix + _inline_to_html(item), s_body))
        elif blk["type"] == "figure":
            fp = FIG_DIR / blk["filename"]
            if fp.exists():
                story.append(Image(str(fp), width=col_w - 4, height=(col_w - 4) * 0.42))
                story.append(Spacer(1, 4))
        elif blk["type"] == "table" and blk["rows"]:
            s_cell = ParagraphStyle("Cell", fontName="Times-Roman", fontSize=6.2, leading=7.5)
            t_rows = [[Paragraph(_inline_to_html(c), s_cell) for c in r] for r in blk["rows"]]
            col_widths = [(col_w - 4) / len(t_rows[0])] * len(t_rows[0])
            tbl = Table(t_rows, colWidths=col_widths)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 5))

    doc.build(story)
    print(f"Generated ReportLab fallback PDF at {PDF_PATH}")


# ---------------------------------------------------------------------------
# 5. Generate True IEEE Two-Column Word (.docx)
# ---------------------------------------------------------------------------

def _set_section_columns(section, num_cols: int, space_twips: int = 320) -> None:
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sectPr.append(cols)
    cols.set(qn("w:num"), str(num_cols))
    cols.set(qn("w:space"), str(space_twips))
    cols.set(qn("w:equalWidth"), "1")


def _configure_margins(section) -> None:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.58)
    section.right_margin = Inches(0.58)


class _DocxRunParser(HTMLParser):
    def __init__(self, p, base_size: float, base_italic: bool, color: RGBColor | None):
        super().__init__(convert_charrefs=True)
        self.p = p
        self.base_size = base_size
        self.color = color
        self.bold = 0
        self.italic = 1 if base_italic else 0
        self.code = 0
        self.sub = 0
        self.sup = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("b", "strong"):
            self.bold += 1
        elif tag in ("i", "em"):
            self.italic += 1
        elif tag == "code":
            self.code += 1
        elif tag == "sub":
            self.sub += 1
        elif tag == "sup":
            self.sup += 1

    def handle_endtag(self, tag):
        if tag in ("b", "strong") and self.bold > 0:
            self.bold -= 1
        elif tag in ("i", "em") and self.italic > 0:
            self.italic -= 1
        elif tag == "code" and self.code > 0:
            self.code -= 1
        elif tag == "sub" and self.sub > 0:
            self.sub -= 1
        elif tag == "sup" and self.sup > 0:
            self.sup -= 1

    def handle_data(self, data):
        if not data:
            return
        run = self.p.add_run(data)
        run.bold = self.bold > 0
        run.italic = self.italic > 0
        is_code = self.code > 0
        run.font.name = "Consolas" if is_code else "Times New Roman"
        run.font.size = Pt(self.base_size - 0.8 if is_code else self.base_size)
        run.font.subscript = self.sub > 0
        run.font.superscript = self.sup > 0
        if is_code:
            run.font.color.rgb = RGBColor(30, 58, 138)
        elif self.color:
            run.font.color.rgb = self.color


def _add_inline_runs_docx(p, raw_md_text: str, base_size: float = 9.5, base_italic: bool = False, color: RGBColor | None = None) -> None:
    """Parse Markdown + inline math identically to HTML output into formatted Word runs."""
    formatted_html = _inline_to_html(raw_md_text, allow_wbr=False)
    parser = _DocxRunParser(p, base_size, base_italic, color)
    parser.feed(formatted_html)
    parser.close()


def _style_ieee_docx_table(table, rows: list[list[str]], full_width_inches: float) -> None:
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ncols = len(rows[0])
    # Clear vertical borders cleanly for booktabs academic style
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>'
        '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        '<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)

    font_sz = 7.5 if ncols >= 7 else 8.0
    col_w = Inches(full_width_inches / ncols)

    for r_idx, row_vals in enumerate(rows):
        row = table.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = col_w
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            tcPr = cell._tc.get_or_add_tcPr()
            if r_idx == 0:
                tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>'))
                tcPr.append(parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="475569"/>'
                    '</w:tcBorders>'
                ))
            elif r_idx % 2 == 0:
                tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="FAFAFA"/>'))

            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            if ncols == 8 and c_idx == 7:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            _add_inline_runs_docx(p, val, base_size=font_sz)
            if r_idx == 0:
                for run in p.runs:
                    run.bold = True


def generate_docx(doc_data: dict) -> None:
    doc = docx.Document()
    sec0 = doc.sections[0]
    _configure_margins(sec0)
    _set_section_columns(sec0, 1)

    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Times New Roman"
    style_normal.font.size = Pt(9.5)

    # Full-width IEEE Banner
    p_banner = doc.add_paragraph()
    p_banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_banner.paragraph_format.space_after = Pt(3)
    rb = p_banner.add_run("BENNETT UNIVERSITY  |  CSET 346 – NATURAL LANGUAGE PROCESSING  |  PROJECT REPORT (PJ_08)")
    rb.font.name = "Times New Roman"
    rb.font.size = Pt(8)
    rb.font.color.rgb = RGBColor(51, 65, 85)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(5)
    rt = p_title.add_run(doc_data["title"])
    rt.bold = True
    rt.font.name = "Times New Roman"
    rt.font.size = Pt(18)
    rt.font.color.rgb = RGBColor(15, 23, 42)

    for hl in doc_data["header_lines"]:
        pm = doc.add_paragraph()
        pm.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pm.paragraph_format.space_before = Pt(0)
        pm.paragraph_format.space_after = Pt(1.5)
        _add_inline_runs_docx(pm, hl, base_size=9.0, color=RGBColor(30, 41, 59))

    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(5)
    p_abs.paragraph_format.space_after = Pt(3)
    r_albl = p_abs.add_run("Abstract—")
    r_albl.bold = True
    r_albl.italic = True
    r_albl.font.name = "Times New Roman"
    r_albl.font.size = Pt(9.0)
    _add_inline_runs_docx(p_abs, doc_data["abstract"], base_size=9.0)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_kw.paragraph_format.space_after = Pt(6)
    r_klbl = p_kw.add_run("Index Terms—")
    r_klbl.bold = True
    r_klbl.italic = True
    r_klbl.font.name = "Times New Roman"
    r_klbl.font.size = Pt(8.8)
    _add_inline_runs_docx(p_kw, doc_data["keywords"], base_size=8.8)

    # Switch to 2-column IEEE body
    cur_sec = doc.add_section(WD_SECTION.CONTINUOUS)
    _configure_margins(cur_sec)
    _set_section_columns(cur_sec, 2)
    current_cols = 2
    fig_counter = 0

    def ensure_cols(n: int) -> None:
        nonlocal current_cols
        if current_cols != n:
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            _configure_margins(sec)
            _set_section_columns(sec, n)
            current_cols = n

    for blk in doc_data["blocks"]:
        btype = blk["type"]
        if btype == "h1":
            ensure_cols(2)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(blk["text"].upper())
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
        elif btype == "h2":
            ensure_cols(2)
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            _add_inline_runs_docx(p, blk["text"], base_size=9.5, base_italic=True)
            for run in p.runs:
                run.bold = True
                run.italic = True
        elif btype == "para":
            ensure_cols(2)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            is_note = blk["text"].startswith("*Note:") or blk["text"].startswith("*†")
            p.paragraph_format.space_after = Pt(4)
            if not is_note:
                p.paragraph_format.first_line_indent = Inches(0.14)
            _add_inline_runs_docx(p, blk["text"], base_size=8.2 if is_note else 9.3)
        elif btype == "list":
            ensure_cols(2)
            for idx, item in enumerate(blk["items"], 1):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Inches(0.18)
                p.paragraph_format.first_line_indent = Inches(-0.12)
                p.paragraph_format.space_after = Pt(2.5)
                prefix = f"{idx}. " if blk["ordered"] else "• "
                r_pre = p.add_run(prefix)
                r_pre.bold = True
                r_pre.font.name = "Times New Roman"
                r_pre.font.size = Pt(9.2)
                _add_inline_runs_docx(p, item, base_size=9.2)
        elif btype == "equation":
            ensure_cols(2)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            _add_inline_runs_docx(p, f"$${blk['expr']}$$", base_size=9.3)
        elif btype == "ref":
            ensure_cols(2)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.20)
            p.paragraph_format.first_line_indent = Inches(-0.20)
            p.paragraph_format.space_after = Pt(3)
            _add_inline_runs_docx(p, blk["text"], base_size=8.3)
        elif btype == "figure":
            fig_counter += 1
            fp = FIG_DIR / blk["filename"]
            ensure_cols(1)
            if fp.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(4)
                p_img.paragraph_format.space_after = Pt(2)
                p_img.paragraph_format.keep_with_next = True
                p_img.add_run().add_picture(str(fp), width=Inches(6.85))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(6)
            rc = p_cap.add_run(f"Fig. {fig_counter}. ")
            rc.bold = True
            rc.font.name = "Times New Roman"
            rc.font.size = Pt(8.3)
            _add_inline_runs_docx(p_cap, blk["caption"], base_size=8.3)
            ensure_cols(2)
        elif btype == "table" and blk["rows"]:
            ncols = len(blk["rows"][0])
            wide = ncols >= 5 or "TABLE IV:" in blk["caption"]
            ensure_cols(1 if wide else 2)
            if blk["caption"]:
                pc = doc.add_paragraph()
                pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pc.paragraph_format.space_before = Pt(4)
                pc.paragraph_format.space_after = Pt(2)
                pc.paragraph_format.keep_with_next = True
                _add_inline_runs_docx(pc, f"**{blk['caption']}**", base_size=8.4)
            tbl = doc.add_table(rows=len(blk["rows"]), cols=ncols)
            width_in = 7.25 if wide else 3.45
            _style_ieee_docx_table(tbl, blk["rows"], width_in)
            sp = doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(4)
            ensure_cols(2)

    doc.save(str(DOCX_PATH))
    print(f"Successfully generated IEEE two-column Word (.docx) at {DOCX_PATH}")


if __name__ == "__main__":
    generate_all_figures()
    parsed = parse_markdown_paper(MD_PATH)
    generate_docx(parsed)
    generate_pdf(parsed)
