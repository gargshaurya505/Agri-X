#!/usr/bin/env python3
"""External validation script for PlantDoc dataset."""

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
    plantdoc_metadata_file = root / "data" / "metadata" / "plantdoc_metadata.json"
    output_dir = root / "reports" / "external_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AGRI-X EXTERNAL EVALUATION: PLANTDOC BENCHMARK")
    print("=" * 70)

    if not checkpoint_path.exists():
        print(f"Error: Model checkpoint not found at {checkpoint_path}")
        sys.exit(1)

    device = get_device()
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
    num_classes = checkpoint["num_classes"]

    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    with open(plantdoc_metadata_file, "r", encoding="utf-8") as f:
        pd_data = json.load(f)

    confirmed_records = pd_data.get("confirmed", [])
    excluded_records = pd_data.get("uncertain_or_excluded", [])

    print(f"Confirmed PlantDoc test samples: {len(confirmed_records)}")
    print(f"Excluded/Ambiguous samples:      {len(excluded_records)}")

    pd_dataset = AgriLeafDataset(
        manifest_path_or_records=confirmed_records,
        transform=get_transforms("test"),
    )
    pd_loader = torch.utils.data.DataLoader(
        pd_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=0,
    )

    eval_results = evaluate_model(model, pd_loader, device, class_mapping)

    overall = eval_results["overall_metrics"]
    print("\n[PlantDoc External Evaluation Metrics]")
    print(f"  Accuracy:         {overall['accuracy'] * 100:.2f}%")
    print(f"  Macro Precision:  {overall['macro_precision'] * 100:.2f}%")
    print(f"  Macro Recall:     {overall['macro_recall'] * 100:.2f}%")
    print(f"  Macro F1:         {overall['macro_f1'] * 100:.2f}%")
    print(f"  Weighted F1:      {overall['weighted_f1'] * 100:.2f}%")

    report_file = output_dir / "plantdoc_metrics.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    plot_paths = save_evaluation_plots(eval_results, output_dir, prefix="plantdoc_external")

    md_summary = f"""# PlantDoc External Evaluation & Domain Shift Analysis

This report analyzes the generalization of the AGRI-X ResNet18 model (trained on lab-conditioned PlantVillage benchmark) when deployed on real-world in-the-wild photography from PlantDoc.

- **Accuracy:** {overall['accuracy'] * 100:.2f}%
- **Macro Precision:** {overall['macro_precision'] * 100:.2f}%
- **Macro Recall:** {overall['macro_recall'] * 100:.2f}%
- **Macro F1 Score:** {overall['macro_f1'] * 100:.2f}%
- **Weighted F1 Score:** {overall['weighted_f1'] * 100:.2f}%

- **`Tomato leaf` (63 images):** Excluded because generic naming does not reliably verify health.
- **`Tomato two spotted spider mites leaf` (2 images):** Insufficient sample size for statistically meaningful performance evaluation.
- **`Tomato Target Spot`:** Not present in the PlantDoc collection.

1. **Background Variance:** PlantVillage images feature homogeneous lab backgrounds (neutral grey/black cards), whereas PlantDoc photos contain complex field soils, dynamic sunlight glare, and mixed foliage.
2. **Multi-Scale Symptoms:** Real field conditions present multiple leaves per shot at varying focal depths, contrasting with PlantVillage's single-leaf centered framing.
3. **Co-infections & Occlusions:** Field leaves frequently display mechanical damage and secondary saprophytic fungi that do not appear in controlled lab culture datasets.
"""
    with open(output_dir / "external_validation_report.md", "w", encoding="utf-8") as f:
        f.write(md_summary)

    print(f"\nSaved external validation reports and figures to: {output_dir}")


if __name__ == "__main__":
    run()
