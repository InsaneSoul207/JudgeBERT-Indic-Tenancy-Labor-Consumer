"""
Training and Fine-Tuning Pipeline for Multilingual JUDGEBERT
Optimizes joint regression and classification objectives for Legal Meaning Preservation.
"""

import os
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, get_linear_schedule_with_warmup

# Local imports
from src.model import MultilingualJudgeBert, DECISION_MAP, ERROR_MAP
from src.evaluate import compute_regression_metrics, compute_classification_metrics

os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["HF_HUB_CACHE"] = os.path.expanduser("~/.cache/huggingface/hub")

class LegalLMPDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=128):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        orig = str(row["original"])
        simp = str(row["simplified"])
        
        inputs = self.tokenizer(
            orig,
            simp,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )
        
        lmp_score = float(row["lmp_score"])
        dec_label = DECISION_MAP.get(row["decision"], 0)
        err_label = ERROR_MAP.get(row.get("error_category", "none"), 0)
        
        item = {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "lmp_score": torch.tensor(lmp_score, dtype=torch.float),
            "dec_label": torch.tensor(dec_label, dtype=torch.long),
            "err_label": torch.tensor(err_label, dtype=torch.long)
        }
        if "token_type_ids" in inputs:
            item["token_type_ids"] = inputs["token_type_ids"].squeeze(0)
            
        return item

def train_model(
    train_path="data/train.csv",
    val_path="data/val.csv",
    output_dir="models",
    base_model="sentence-transformers/all-MiniLM-L6-v2",
    epochs=6,
    batch_size=8,
    lr=2e-5,
    seed=42
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training Multilingual JUDGEBERT on device: {device}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = MultilingualJudgeBert(base_model_name=base_model)
    model.to(device)
    
    train_dataset = LegalLMPDataset(train_df, tokenizer)
    val_dataset = LegalLMPDataset(val_df, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Loss functions
    mse_criterion = nn.MSELoss()
    huber_criterion = nn.SmoothL1Loss()
    
    # Dynamic class-weighting for decision head to solve minority-class underfitting
    dec_counts = train_df["decision"].map(DECISION_MAP).value_counts()
    n_classes = len(DECISION_MAP)
    total_samples = len(train_df)
    dec_weights = torch.tensor(
        [total_samples / (n_classes * dec_counts.get(i, 1)) for i in range(n_classes)],
        dtype=torch.float,
        device=device
    )
    dec_weights = dec_weights / dec_weights.mean()
    ce_dec_criterion = nn.CrossEntropyLoss(weight=dec_weights)
    ce_err_criterion = nn.CrossEntropyLoss()
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps)
    
    best_val_pearson = -1.0
    history = []
    
    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0
        
        for batch in train_loader:
            optimizer.zero_grad()
            
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch.get("token_type_ids")
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(device)
                
            targets_lmp = batch["lmp_score"].to(device)
            targets_dec = batch["dec_label"].to(device)
            targets_err = batch["err_label"].to(device)
            
            outputs = model(input_ids, attention_mask, token_type_ids)
            
            loss_reg = huber_criterion(outputs["pred_lmp"], targets_lmp)
            loss_dec = ce_dec_criterion(outputs["decision_logits"], targets_dec)
            loss_err = ce_err_criterion(outputs["error_logits"], targets_err)
            
            # Dual-head ordinal consistency constraint:
            # Penalize continuous score spilling over ordinal thresholds when contradicted by ground truth
            pred_lmp = outputs["pred_lmp"]
            loss_cons = (
                torch.relu(pred_lmp - 4.0) * (targets_dec == 0).float() +
                torch.relu(8.0 - pred_lmp) * (targets_dec == 2).float()
            ).mean()
            
            # Rebalanced multi-task loss with enhanced categorical alignment and consistency
            loss = loss_reg + 0.8 * loss_dec + 0.5 * loss_err + 0.3 * loss_cons
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            
            total_train_loss += loss.item()
            
        avg_train_loss = total_train_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_preds, val_targets = [], []
        val_dec_preds, val_dec_targets = [], []
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                token_type_ids = batch.get("token_type_ids")
                if token_type_ids is not None:
                    token_type_ids = token_type_ids.to(device)
                    
                outputs = model(input_ids, attention_mask, token_type_ids)
                
                val_preds.extend(outputs["pred_lmp"].cpu().numpy().tolist())
                val_targets.extend(batch["lmp_score"].numpy().tolist())
                
                dec_p = torch.argmax(outputs["decision_logits"], dim=-1).cpu().numpy().tolist()
                val_dec_preds.extend(dec_p)
                val_dec_targets.extend(batch["dec_label"].numpy().tolist())
                
        reg_metrics = compute_regression_metrics(val_targets, val_preds)
        val_acc = (np.array(val_dec_preds) == np.array(val_dec_targets)).mean()
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train_loss:.4f} | Val Pearson r: {reg_metrics['pearson_r']:.4f} | Val RMSE: {reg_metrics['rmse']:.4f} | Val Acc: {val_acc:.4f}", flush=True)
        
        epoch_stats = {
            "epoch": epoch,
            "train_loss": avg_train_loss,
            "val_pearson_r": reg_metrics["pearson_r"],
            "val_rmse": reg_metrics["rmse"],
            "val_accuracy": float(val_acc)
        }
        history.append(epoch_stats)
        
        # Checkpoint best model
        if reg_metrics["pearson_r"] > best_val_pearson:
            best_val_pearson = reg_metrics["pearson_r"]
            best_model_path = os.path.join(output_dir, "best_judgebert.pt")
            torch.save(model.state_dict(), best_model_path)
            print(f"  -> Saved new best checkpoint to {best_model_path} (Pearson r = {best_val_pearson:.4f})", flush=True)
            
    with open(os.path.join(output_dir, "training_history.json"), "w") as f:
        json.dump(history, f, indent=2)
        
    print(f"\nTraining Complete. Best Validation Pearson r: {best_val_pearson:.4f}", flush=True)
    return os.path.join(output_dir, "best_judgebert.pt")

if __name__ == "__main__":
    train_model(epochs=6, batch_size=8)
