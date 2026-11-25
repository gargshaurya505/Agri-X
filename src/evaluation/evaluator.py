"""Comprehensive evaluation module for AGRI-X.

Calculates:
- Accuracy, Macro/Weighted Precision, Recall, F1
- Per-class classification report
- Confusion matrices (raw counts and normalized percentages)
- Misclassified sample analysis with confidence scores
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score


@torch.no_grad()
def evaluate_model(
    model: nn.Module,
    data_loader: torch.utils.data.DataLoader,
    device: torch.device,
    class_mapping: Dict[int, str],
) -> Dict[str, Any]:
    """Evaluate model on a DataLoader, returning predictions, probabilities, targets, and metrics."""
    model.eval()
    model.to(device)

    all_targets = []
    all_preds = []
    all_probs = []
    all_paths = []

    for images, targets, paths in data_loader:
        images = images.to(device)
        outputs = model(images)
        probs = torch.softmax(outputs, dim=1)
        preds = outputs.argmax(dim=1)

        all_targets.extend(targets.cpu().numpy().tolist())
        all_preds.extend(preds.cpu().numpy().tolist())
        all_probs.extend(probs.cpu().numpy().tolist())
        all_paths.extend(paths)

    all_targets = np.array(all_targets)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    acc = accuracy_score(all_targets, all_preds)
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(all_targets, all_preds, average="weighted", zero_division=0)
    macro_prec = precision_score(all_targets, all_preds, average="macro", zero_division=0)
    macro_rec = recall_score(all_targets, all_preds, average="macro", zero_division=0)

    labels = sorted(list(class_mapping.keys()))
    target_names = [class_mapping[k] for k in labels]
    report_dict = classification_report(
        all_targets,
        all_preds,
        labels=labels,
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(all_targets, all_preds, labels=labels)
    cm_norm = confusion_matrix(all_targets, all_preds, labels=labels, normalize="true")

    misclassified = []
    for i in range(len(all_targets)):
        if all_targets[i] != all_preds[i]:
            true_cls = class_mapping.get(int(all_targets[i]), str(all_targets[i]))
            pred_cls = class_mapping.get(int(all_preds[i]), str(all_preds[i]))
            conf = float(all_probs[i][all_preds[i]])
            misclassified.append({
                "file_path": all_paths[i],
                "true_class_id": int(all_targets[i]),
                "true_class_name": true_cls,
                "pred_class_id": int(all_preds[i]),
                "pred_class_name": pred_cls,
                "confidence": conf,
            })

    misclassified.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "overall_metrics": {
            "accuracy": float(acc),
            "macro_precision": float(macro_prec),
            "macro_recall": float(macro_rec),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "total_samples": int(len(all_targets)),
            "misclassified_samples_count": int(len(misclassified)),
        },
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_normalized": cm_norm.tolist(),
        "misclassified": misclassified,
        "target_names": target_names,
    }


def save_evaluation_plots(
    eval_results: Dict[str, Any],
    output_dir: str | Path,
    prefix: str = "internal_test",
) -> Dict[str, Path]:
    """Generate and save publication-grade confusion matrices and confidence charts."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    target_names = eval_results["target_names"]
    cm = np.array(eval_results["confusion_matrix"])
    cm_norm = np.array(eval_results["confusion_matrix_normalized"])

    fig_cm_path = out_path / f"{prefix}_confusion_matrix.png"
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=target_names,
        yticklabels=target_names,
    )
    plt.title(f"Confusion Matrix (Counts) - {prefix.replace('_', ' ').title()}", fontsize=14, pad=12)
    plt.xlabel("Predicted Class", fontsize=12)
    plt.ylabel("True Class", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(fig_cm_path, dpi=300)
    plt.close()

    fig_norm_path = out_path / f"{prefix}_confusion_matrix_normalized.png"
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm_norm,
        annot=True,
        fmt=".2f",
        cmap="Greens",
        xticklabels=target_names,
        yticklabels=target_names,
    )
    plt.title(f"Normalized Confusion Matrix - {prefix.replace('_', ' ').title()}", fontsize=14, pad=12)
    plt.xlabel("Predicted Class", fontsize=12)
    plt.ylabel("True Class", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(fig_norm_path, dpi=300)
    plt.close()

    return {
        "confusion_matrix": fig_cm_path,
        "confusion_matrix_normalized": fig_norm_path,
    }
