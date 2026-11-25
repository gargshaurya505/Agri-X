#!/usr/bin/env python3
"""Misclassification and Error Analysis script for AGRI-X.

Reads internal test set evaluation predictions, identifies false predictions
(both high-confidence and low-confidence errors), generates comparative
Grad-CAM panels (true vs predicted classes), and generates structured error analysis.
"""

import csv
import json
import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root
from src.utils.device import get_device
from src.models.resnet18 import build_model
from src.explainability.explanation_service import ExplanationService


def main():
    root = get_project_root()
    test_metrics_file = root / "reports" / "metrics" / "internal_test_metrics.json"
    checkpoint_path = root / "models" / "best_resnet18.pth"
    output_dir = root / "reports" / "figures" / "misclassifications"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_out = root / "reports" / "explainability" / "misclassified_examples.csv"
    csv_out.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AGRI-X MISCLASSIFICATION & ERROR ATTRIBUTION ANALYSIS")
    print("=" * 70)

    if not test_metrics_file.exists():
        print(f"Error: {test_metrics_file} not found. Run evaluate_model.py first.")
        sys.exit(1)

    with open(test_metrics_file, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    misclassified = metrics.get("misclassified", [])
    print(f"Total misclassifications recorded on internal test set: {len(misclassified)}")

    device = get_device()
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
    num_classes = checkpoint["num_classes"]

    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    service = ExplanationService(model=model, class_mapping=class_mapping, device=device)

    high_conf_errors = [m for m in misclassified if m["confidence"] >= 0.80]
    low_conf_errors = [m for m in misclassified if m["confidence"] < 0.80]

    print(f"  High-confidence errors (>=80% conf): {len(high_conf_errors)}")
    print(f"  Low-confidence errors (<80% conf):   {len(low_conf_errors)}")

    selected = high_conf_errors[:5] + low_conf_errors[:5]

    records = []
    for item in selected:
        img_path = item["file_path"]
        true_name = item["true_class_name"]
        pred_name = item["pred_class_name"]
        conf = item["confidence"]

        result_pred = service.explain_image(img_path, target_class=item["pred_class_id"])
        stem = Path(img_path).stem.replace(" ", "_")
        panel_name = f"error_true_{true_name.replace(' ', '_')}_pred_{pred_name.replace(' ', '_')}_{stem[:16]}.png"
        panel_path = output_dir / panel_name

        service.save_explanation_panel(result_pred, panel_path)

        result_true = service.explain_image(img_path, target_class=item["true_class_id"])
        true_panel_name = f"counterfactual_true_{true_name.replace(' ', '_')}_{stem[:16]}.png"
        true_panel_path = output_dir / true_panel_name
        service.save_explanation_panel(result_true, true_panel_path)

        records.append({
            "image_path": img_path,
            "true_class_id": item["true_class_id"],
            "true_class_name": true_name,
            "pred_class_id": item["pred_class_id"],
            "pred_class_name": pred_name,
            "confidence": conf,
            "predicted_panel_path": str(panel_path),
            "counterfactual_panel_path": str(true_panel_path),
        })

    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "true_class_id", "true_class_name",
            "pred_class_id", "pred_class_name", "confidence",
            "predicted_panel_path", "counterfactual_panel_path"
        ])
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"\nGenerated misclassification and counterfactual panels in: {output_dir}")
    print(f"Saved misclassification CSV: {csv_out}")


if __name__ == "__main__":
    main()
