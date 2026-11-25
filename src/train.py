"""
Training and Fine-Tuning Pipeline for Multilingual JUDGEBERT
Optimizes joint regression, ordinal classification, consistency, and cross-lingual objectives
for Legal Meaning Preservation (GPU-accelerated).
"""

import os
os.environ["USE_TF"] = "0"
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup

from src.model import (
    MultilingualJudgeBert,
    DECISION_MAP,
    ERROR_MAP,
    preprocess_legal_text
)
from src.evaluate import compute_regression_metrics


class LegalLMPDataset(Dataset):
    """Vectorized pre-tokenized dataset with lossless Hindi phonetic normalization."""
    def __init__(self, df, tokenizer, max_len=256, transliterate_hindi=True):
        self.df = df.reset_index(drop=True)
        origs = [preprocess_legal_text(x, transliterate_hindi) for x in self.df["original"].astype(str).tolist()]
        simps = [preprocess_legal_text(x, transliterate_hindi) for x in self.df["simplified"].astype(str).tolist()]

        enc = tokenizer(
            origs,
            simps,
            padding="max_length",
            truncation=True,
            max_length=max_len,
            return_tensors="pt"
        )
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.token_type_ids = enc.get("token_type_ids")

        self.lmp_scores = torch.tensor(self.df["lmp_score"].astype(float).values, dtype=torch.float)
        self.dec_labels = torch.tensor(
            [DECISION_MAP.get(d, 0) for d in self.df["decision"].tolist()], dtype=torch.long
        )
        self.err_labels = torch.tensor(
            [ERROR_MAP.get(e, 0) for e in self.df.get("error_category", ["none"] * len(self.df)).tolist()],
            dtype=torch.long
        )
        self.is_hindi = torch.tensor(
            [1.0 if str(l).lower().startswith("hi") else 0.0 for l in self.df.get("language", ["en"] * len(self.df)).tolist()],
            dtype=torch.float
        )

    def __len__(self):
        return len(self.lmp_scores)

    def __getitem__(self, idx):
        item = {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "lmp_score": self.lmp_scores[idx],
            "dec_label": self.dec_labels[idx],
            "err_label": self.err_labels[idx],
            "is_hindi": self.is_hindi[idx]
        }
        if self.token_type_ids is not None:
            item["token_type_ids"] = self.token_type_ids[idx]
        return item


def _augment_train_contrastive_pairs(train_df, seed=42):
    """
    Strictly augments ONLY train_df with verbatim identity, cross-clause mismatch,
    and hard numeric contrast pairs to prevent clause-topic memorization.
    Never touches val or test splits.
    """
    rng = np.random.default_rng(seed)
    aug_rows = []
    grouped = train_df.groupby("original")

    # 1. Verbatim identity pairs (prevents negative-topic bias on identical clauses)
    hi_origs = train_df[train_df["language"] == "hi"]["original"].unique().tolist()
    en_origs = train_df[train_df["language"] == "en"]["original"].unique().tolist()
    rng.shuffle(hi_origs)
    rng.shuffle(en_origs)

    for orig_list, lang_code, limit in [(hi_origs, "hi", 110), (en_origs, "en", 90)]:
        for orig in orig_list[:limit]:
            dom = train_df[train_df["original"] == orig]["domain"].iloc[0]
            aug_rows.append({
                "id": f"AUG-ID-{len(aug_rows)+1}",
                "language": lang_code,
                "domain": dom,
                "original": orig,
                "simplified": orig,
                "lmp_score": 9.8,
                "decision": "Preserved",
                "error_category": "none"
            })

    # 2. Cross-clause unrelated pairs within same language (prevents positive-topic bias)
    for orig_list, lang_code, limit in [(hi_origs, "hi", 80), (en_origs, "en", 70)]:
        if len(orig_list) >= 4:
            for i in range(min(limit, len(orig_list))):
                j = (i + len(orig_list) // 2 + 1) % len(orig_list)
                o1, o2 = orig_list[i], orig_list[j]
                if o1[:25] != o2[:25]:
                    dom = train_df[train_df["original"] == o1]["domain"].iloc[0]
                    aug_rows.append({
                        "id": f"AUG-UN-{len(aug_rows)+1}",
                        "language": lang_code,
                        "domain": dom,
                        "original": o1,
                        "simplified": o2,
                        "lmp_score": 1.1,
                        "decision": "Not Preserved",
                        "error_category": "contradiction"
                    })

    # 3. Numeric hard negatives for Preserved-only numeric clauses in train_df
    for orig, grp in grouped:
        decs = set(grp["decision"].tolist())
        if decs == {"Preserved"}:
            row0 = grp.iloc[0]
            simp = str(row0["simplified"])
            nums = re.findall(r"\b\d+\b", simp)
            if nums:
                n0 = nums[0]
                alt = str(int(n0) + 12) if int(n0) < 1900 else str(int(n0) + 20)
                aug_rows.append({
                    "id": f"AUG-NUM-{len(aug_rows)+1}",
                    "language": row0["language"],
                    "domain": row0["domain"],
                    "original": orig,
                    "simplified": simp.replace(n0, alt, 1),
                    "lmp_score": 2.0,
                    "decision": "Not Preserved",
                    "error_category": "date_number"
                })

    if not aug_rows:
        return train_df
    df_aug = pd.DataFrame(aug_rows)
    return pd.concat([train_df, df_aug], ignore_index=True)


def train_model(
    train_path="data/train.csv",
    val_path="data/val.csv",
    output_dir="models",
    base_model="sentence-transformers/all-MiniLM-L6-v2",
    epochs=12,
    batch_size=16,
    lr=3e-5,
    seed=42,
    transliterate_hindi=True,
    augment_contrastive=True
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu_info = f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""
    print(f"Training Multilingual JUDGEBERT on device: {device}{gpu_info}", flush=True)

    os.makedirs(output_dir, exist_ok=True)

    train_df = pd.read_csv(train_path)
    if augment_contrastive:
        base_n = len(train_df)
        train_df = _augment_train_contrastive_pairs(train_df, seed=seed)
        print(f"Train split augmented cleanly (train-only): {base_n} -> {len(train_df)} pairs", flush=True)
    val_df = pd.read_csv(val_path)

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = MultilingualJudgeBert(base_model_name=base_model)
    model.to(device)

    train_dataset = LegalLMPDataset(train_df, tokenizer, max_len=256, transliterate_hindi=transliterate_hindi)
    val_dataset = LegalLMPDataset(val_df, tokenizer, max_len=256, transliterate_hindi=transliterate_hindi)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, pin_memory=(device.type == "cuda"))
    val_loader = DataLoader(val_dataset, batch_size=batch_size * 2, shuffle=False, pin_memory=(device.type == "cuda"))

    # Per-sample losses for true sample-level Hindi weighting
    huber_criterion = nn.SmoothL1Loss(reduction="none")

    # Tempered inverse-frequency class weights (exponent 0.65 prevents minority collapse while preserving boundary precision)
    dec_counts = train_df["decision"].map(DECISION_MAP).value_counts()
    n_classes = len(DECISION_MAP)
    total_samples = len(train_df)
    dec_weights = torch.tensor(
        [(total_samples / (n_classes * dec_counts.get(i, 1))) ** 0.65 for i in range(n_classes)],
        dtype=torch.float,
        device=device
    )
    dec_weights = dec_weights / dec_weights.mean()
    ce_dec_criterion = nn.CrossEntropyLoss(weight=dec_weights, reduction="none")
    ce_err_criterion = nn.CrossEntropyLoss(reduction="none")

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps
    )

    best_score = -1.0
    best_val_pearson = -1.0
    history = []

    val_langs = val_df.get("language", pd.Series(["en"] * len(val_df))).astype(str).values

    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0

        for batch in train_loader:
            optimizer.zero_grad()

            input_ids = batch["input_ids"].to(device, non_blocking=True)
            attention_mask = batch["attention_mask"].to(device, non_blocking=True)
            token_type_ids = batch.get("token_type_ids")
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(device, non_blocking=True)

            targets_lmp = batch["lmp_score"].to(device, non_blocking=True)
            targets_dec = batch["dec_label"].to(device, non_blocking=True)
            targets_err = batch["err_label"].to(device, non_blocking=True)
            is_hindi = batch["is_hindi"].to(device, non_blocking=True)

            outputs = model(input_ids, attention_mask, token_type_ids)

            loss_reg_vec = huber_criterion(outputs["pred_lmp"], targets_lmp)
            loss_dec_vec = ce_dec_criterion(outputs["decision_logits"], targets_dec)
            loss_err_vec = ce_err_criterion(outputs["error_logits"], targets_err)

            # Dual-head ordinal consistency constraint
            pred_lmp = outputs["pred_lmp"]
            loss_cons_vec = (
                torch.relu(pred_lmp - 4.0) * (targets_dec == 0).float() +
                torch.relu(8.0 - pred_lmp) * (targets_dec == 2).float()
            )

            # Per-sample Hindi gradient multiplier (1.5x weight for Hindi statutory clauses)
            lang_weights = 1.0 + 0.5 * is_hindi
            loss_per_sample = loss_reg_vec + 0.85 * loss_dec_vec + 0.5 * loss_err_vec + 0.35 * loss_cons_vec
            loss = (loss_per_sample * lang_weights).mean()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / max(1, len(train_loader))

        # Validation
        model.eval()
        val_preds, val_targets = [], []
        val_dec_preds, val_dec_targets = [], []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device, non_blocking=True)
                attention_mask = batch["attention_mask"].to(device, non_blocking=True)
                token_type_ids = batch.get("token_type_ids")
                if token_type_ids is not None:
                    token_type_ids = token_type_ids.to(device, non_blocking=True)

                outputs = model(input_ids, attention_mask, token_type_ids)

                val_preds.extend(outputs["pred_lmp"].cpu().numpy().tolist())
                val_targets.extend(batch["lmp_score"].numpy().tolist())

                dec_p = torch.argmax(outputs["decision_logits"], dim=-1).cpu().numpy().tolist()
                val_dec_preds.extend(dec_p)
                val_dec_targets.extend(batch["dec_label"].numpy().tolist())

        reg_metrics = compute_regression_metrics(val_targets, val_preds)
        val_preds_arr = np.array(val_preds)
        val_targets_arr = np.array(val_targets)
        val_acc = float((np.array(val_dec_preds) == np.array(val_dec_targets)).mean())
        val_macro_f1 = float(f1_score(val_dec_targets, val_dec_preds, average="macro", zero_division=0))

        en_mask = (val_langs == "en")
        hi_mask = (val_langs == "hi")
        en_r = compute_regression_metrics(val_targets_arr[en_mask], val_preds_arr[en_mask])["pearson_r"] if en_mask.sum() > 2 else 0.0
        hi_r = compute_regression_metrics(val_targets_arr[hi_mask], val_preds_arr[hi_mask])["pearson_r"] if hi_mask.sum() > 2 else 0.0

        print(
            f"Epoch {epoch:02d}/{epochs:02d} | Loss: {avg_train_loss:.4f} | "
            f"Val r: {reg_metrics['pearson_r']:.4f} (EN: {en_r:.4f}, HI: {hi_r:.4f}) | "
            f"RMSE: {reg_metrics['rmse']:.4f} | Acc: {val_acc:.4f} | F1: {val_macro_f1:.4f}",
            flush=True
        )

        epoch_stats = {
            "epoch": epoch,
            "train_loss": avg_train_loss,
            "val_pearson_r": reg_metrics["pearson_r"],
            "val_en_pearson_r": en_r,
            "val_hi_pearson_r": hi_r,
            "val_rmse": reg_metrics["rmse"],
            "val_accuracy": val_acc,
            "val_macro_f1": val_macro_f1
        }
        history.append(epoch_stats)

        composite_metric = reg_metrics["pearson_r"] + 0.15 * val_macro_f1
        if composite_metric > best_score:
            best_score = composite_metric
            best_val_pearson = reg_metrics["pearson_r"]
            best_model_path = os.path.join(output_dir, "best_judgebert.pt")
            torch.save(model.state_dict(), best_model_path)
            print(f"  -> Saved new best checkpoint to {best_model_path} (r = {best_val_pearson:.4f}, F1 = {val_macro_f1:.4f})", flush=True)

    with open(os.path.join(output_dir, "training_history.json"), "w") as f:
        json.dump(history, f, indent=2)

    print(f"\nTraining Complete. Best Validation Pearson r: {best_val_pearson:.4f}", flush=True)
    return os.path.join(output_dir, "best_judgebert.pt")


if __name__ == "__main__":
    train_model(epochs=10, batch_size=16)
