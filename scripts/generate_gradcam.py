#!/usr/bin/env python3
"""Batch Grad-CAM explanation generation script for AGRI-X.

Reads images from a manifest or test split, processes them efficiently
using a single loaded model instance, and outputs visual panels and
structured metadata.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from tqdm import tqdm
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root
from src.utils.device import get_device
from src.models.resnet18 import build_model
from src.explainability.explanation_service import ExplanationService


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Batch Grad-CAM Explanations")
    parser.add_argument("--manifest", type=str, default="data/splits/test.csv", help="CSV manifest of images")
    parser.add_argument("--limit-per-class", type=int, default=2, help="Max explanations to generate per class")
    parser.add_argument("--output-dir", type=str, default="reports/figures/gradcam", help="Output directory for panels")
    parser.add_argument("--metadata-file", type=str, default="reports/explainability/gradcam_metadata.csv", help="Metadata CSV path")
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    checkpoint_path = root / "models" / "best_resnet18.pth"
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_file = root / args.metadata_file
    metadata_file.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AGRI-X BATCH GRAD-CAM EXPLANATION PIPELINE")
    print("=" * 70)

    device = get_device()
    print(f"Device: {device}")
    print(f"Loading checkpoint: {checkpoint_path}")

    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
    num_classes = checkpoint["num_classes"]

    model = build_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)

    service = ExplanationService(model=model, class_mapping=class_mapping, device=device)

    manifest_path = root / args.manifest
    selected_samples = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = int(row["class_id"])
            if cid not in selected_samples:
                selected_samples[cid] = []
            if len(selected_samples[cid]) < args.limit_per_class:
                selected_samples[cid].append(row)

    flattened = [row for rows in selected_samples.values() for row in rows]
    print(f"Selected {len(flattened)} images across {len(selected_samples)} classes (limit: {args.limit_per_class}/class).")

    records = []
    for item in tqdm(flattened, desc="Generating Explanations"):
        img_path = item["file_path"]
        cid = int(item["class_id"])
        cname = item["class_name"]

        try:
            result = service.explain_image(img_path)
            stem = Path(img_path).stem.replace(" ", "_")
            out_img_name = f"cam_c{cid}_{result.predicted_class_name.replace(' ', '_')}_{stem[:16]}.png"
            out_panel_path = output_dir / out_img_name

            service.save_explanation_panel(result, out_panel_path)

            records.append({
                "image_path": img_path,
                "ground_truth_class_id": cid,
                "ground_truth_class_name": cname,
                "predicted_class_id": result.predicted_class_id,
                "predicted_class_name": result.predicted_class_name,
                "confidence": result.confidence,
                "is_correct": (cid == result.predicted_class_id),
                "panel_path": str(out_panel_path),
                "top2_class": result.top_k_predictions[1]["class_name"] if len(result.top_k_predictions) > 1 else "",
                "top2_prob": result.top_k_predictions[1]["probability"] if len(result.top_k_predictions) > 1 else 0.0,
            })
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    with open(metadata_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "image_path", "ground_truth_class_id", "ground_truth_class_name",
            "predicted_class_id", "predicted_class_name", "confidence",
            "is_correct", "panel_path", "top2_class", "top2_prob"
        ])
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"\nBatch processing complete. Generated {len(records)} visual panels.")
    print(f"Saved panels to: {output_dir}")
    print(f"Saved metadata to: {metadata_file}")


if __name__ == "__main__":
    main()
