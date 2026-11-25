#!/usr/bin/env python3
"""Controlled Perturbation and Robustness Experiment script for AGRI-X.

Evaluates prediction stability, confidence drift, and Grad-CAM consistency under
controlled visual perturbations without mutating original raw dataset files:
- Brightness adjustment (+20%, -20%)
- Contrast adjustment (+20%, -20%)
- Small affine rotation (10 degrees)
- Gaussian blur (mild radius)
- Resolution downscaling (160x160)
"""

import csv
import json
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from tqdm import tqdm
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root
from src.utils.device import get_device
from src.models.resnet18 import build_model
from src.explainability.explanation_service import ExplanationService


def apply_perturbation(img: Image.Image, p_type: str) -> Image.Image:
    """Apply non-destructive in-memory image transformation."""
    if p_type == "brightness_high":
        return ImageEnhance.Brightness(img).enhance(1.25)
    elif p_type == "brightness_low":
        return ImageEnhance.Brightness(img).enhance(0.75)
    elif p_type == "contrast_high":
        return ImageEnhance.Contrast(img).enhance(1.25)
    elif p_type == "contrast_low":
        return ImageEnhance.Contrast(img).enhance(0.75)
    elif p_type == "rotation_10":
        return img.rotate(10, resample=Image.Resampling.BILINEAR)
    elif p_type == "mild_blur":
        return img.filter(ImageFilter.GaussianBlur(radius=1.2))
    elif p_type == "downscale_160":
        down = img.resize((160, 160), resample=Image.Resampling.BILINEAR)
        return down.resize(img.size, resample=Image.Resampling.BILINEAR)
    return img


def main():
    root = get_project_root()
    manifest_file = root / "data" / "splits" / "test.csv"
    checkpoint_path = root / "models" / "best_resnet18.pth"
    output_dir = root / "reports" / "figures" / "robustness"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file = root / "reports" / "explainability" / "robustness_results.csv"
    summary_file = root / "reports" / "explainability" / "robustness_summary.json"

    print("=" * 70)
    print("AGRI-X CONTROLLED PERTURBATION & ROBUSTNESS EXPERIMENTS")
    print("=" * 70)

    device = get_device()
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
    num_classes = checkpoint["num_classes"]

    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    service = ExplanationService(model=model, class_mapping=class_mapping, device=device)

    sampled = {}
    with open(manifest_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = int(row["class_id"])
            if cid not in sampled:
                sampled[cid] = row

    test_images = list(sampled.values())
    print(f"Sampled {len(test_images)} representative test images (1 per class).")

    perturbation_types = [
        "baseline",
        "brightness_high",
        "brightness_low",
        "contrast_high",
        "contrast_low",
        "rotation_10",
        "mild_blur",
        "downscale_160",
    ]

    records = []
    consistency_counts = {p: {"total": 0, "preserved": 0, "conf_drop_sum": 0.0} for p in perturbation_types}

    for item in tqdm(test_images, desc="Running Robustness Trials"):
        img_path = Path(item["file_path"])
        gt_cid = int(item["class_id"])
        gt_cname = item["class_name"]

        with Image.open(img_path) as orig_raw:
            orig_img = orig_raw.convert("RGB")

        base_result = service.explain_image(img_path)
        base_pred_cid = base_result.predicted_class_id
        base_conf = base_result.confidence

        for p_type in perturbation_types:
            if p_type == "baseline":
                p_img = orig_img
            else:
                p_img = apply_perturbation(orig_img, p_type)

            temp_path = output_dir / f"temp_{p_type}_{img_path.name}"
            p_img.save(temp_path)

            p_result = service.explain_image(temp_path)
            temp_path.unlink()

            is_preserved = (p_result.predicted_class_id == base_pred_cid)
            conf_diff = p_result.confidence - base_conf

            consistency_counts[p_type]["total"] += 1
            if is_preserved:
                consistency_counts[p_type]["preserved"] += 1
            consistency_counts[p_type]["conf_drop_sum"] += conf_diff

            if p_type in ["rotation_10", "mild_blur"] and gt_cid in [0, 1]:
                p_panel_name = f"robustness_{p_type}_c{gt_cid}_{img_path.stem[:12]}.png"
                p_panel_path = output_dir / p_panel_name
                service.save_explanation_panel(p_result, p_panel_path)

            records.append({
                "image_path": str(img_path),
                "ground_truth_id": gt_cid,
                "ground_truth_name": gt_cname,
                "perturbation": p_type,
                "baseline_pred_id": base_pred_cid,
                "baseline_confidence": base_conf,
                "perturbed_pred_id": p_result.predicted_class_id,
                "perturbed_pred_name": p_result.predicted_class_name,
                "perturbed_confidence": p_result.confidence,
                "prediction_preserved": is_preserved,
                "confidence_delta": conf_diff,
            })

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "ground_truth_id", "ground_truth_name", "perturbation",
            "baseline_pred_id", "baseline_confidence", "perturbed_pred_id",
            "perturbed_pred_name", "perturbed_confidence", "prediction_preserved",
            "confidence_delta"
        ])
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    summary_report = {}
    print("\n[Robustness Performance Summary]")
    for p, stats in consistency_counts.items():
        rate = stats["preserved"] / stats["total"] * 100 if stats["total"] > 0 else 0
        avg_drift = stats["conf_drop_sum"] / stats["total"] if stats["total"] > 0 else 0
        summary_report[p] = {
            "prediction_retention_rate_pct": rate,
            "mean_confidence_drift": avg_drift,
            "samples_tested": stats["total"],
        }
        print(f"  {p:<16}: Retention = {rate:5.1f}% | Mean Conf Drift = {avg_drift:+.4f}")

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    print(f"\nSaved robustness results to: {csv_file}")
    print(f"Saved robustness summary to: {summary_file}")


if __name__ == "__main__":
    main()
