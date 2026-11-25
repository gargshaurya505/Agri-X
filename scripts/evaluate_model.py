#!/usr/bin/env python3
"""Evaluate saved AGRI-X ResNet18 model on untouched internal test split."""

import json
import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root
from src.utils.device import get_device
from src.data.dataset import AgriLeafDataset, get_transforms
from src.models.resnet18 import build_model
from src.evaluation.evaluator import evaluate_model, save_evaluation_plots


def run():
    root = get_project_root()
    checkpoint_path = root / "models" / "best_resnet18.pth"
    test_manifest = root / "data" / "splits" / "test.csv"
    reports_metrics_dir = root / "reports" / "metrics"
    reports_figures_dir = root / "reports" / "figures"
    reports_metrics_dir.mkdir(parents=True, exist_ok=True)
    reports_figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AGRI-X INTERNAL TEST SET EVALUATION")
    print("=" * 70)

    if not checkpoint_path.exists():
        print(f"Error: Model checkpoint not found at {checkpoint_path}")
        sys.exit(1)

    device = get_device()
    print(f"Device: {device}")
    print(f"Loading checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)

    class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
    num_classes = checkpoint["num_classes"]

    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    test_dataset = AgriLeafDataset(
        manifest_path_or_records=test_manifest,
        transform=get_transforms("test"),
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=64,
        shuffle=False,
        num_workers=0,
    )
    print(f"Evaluating on untouched internal test set: {len(test_dataset)} samples")

    eval_results = evaluate_model(model, test_loader, device, class_mapping)

    overall = eval_results["overall_metrics"]
    print("\n[Internal Test Set Overall Metrics]")
    print(f"  Accuracy:         {overall['accuracy'] * 100:.2f}%")
    print(f"  Macro Precision:  {overall['macro_precision'] * 100:.2f}%")
    print(f"  Macro Recall:     {overall['macro_recall'] * 100:.2f}%")
    print(f"  Macro F1:         {overall['macro_f1'] * 100:.2f}%")
    print(f"  Weighted F1:      {overall['weighted_f1'] * 100:.2f}%")
    print(f"  Misclassifications: {overall['misclassified_samples_count']} / {overall['total_samples']}")

    metrics_file = reports_metrics_dir / "internal_test_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    plot_paths = save_evaluation_plots(eval_results, reports_figures_dir, prefix="internal_test")
    print(f"\nGenerated Plots:")
    for k, p in plot_paths.items():
        print(f"  {k}: {p}")
    print(f"Saved machine-readable metrics: {metrics_file}")


if __name__ == "__main__":
    run()
