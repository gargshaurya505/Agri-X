#!/usr/bin/env python3
"""Run Phase 2 audit on PlantVillage and PlantDoc datasets."""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import load_dataset_config, get_project_root
from src.data.preparation import (
    PlantVillagePreparator,
    PLANTVILLAGE_TOMATO_TAXONOMY,
    PLANTDOC_TOMATO_TAXONOMY,
    inspect_image,
    compute_sha256,
    SUPPORTED_EXTENSIONS,
)

def run():
    root = get_project_root()
    dataset_cfg = load_dataset_config()
    output_audit_dir = root / "reports" / "dataset_audit"
    output_audit_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = root / "data" / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AGRI-X PHASE 2: DATASET AUDIT AND VERIFICATION")
    print("=" * 70)

    pv_cfg = dataset_cfg["datasets"]["plantvillage"]
    pv_raw = root / pv_cfg["raw_path"]
    leaf_map_file = root / pv_cfg.get("leaf_map_path", "")

    print(f"\n[1] Auditing Primary Training Dataset: PlantVillage")
    print(f"Path: {pv_raw}")
    print(f"Leaf-map: {leaf_map_file} (exists: {leaf_map_file.exists()})")

    preparator = PlantVillagePreparator(pv_raw, leaf_map_file)
    audit_results = preparator.audit_and_prepare()

    print(f"  Valid clean images: {audit_results['total_valid_cleaned']}")
    print(f"  Corrupted files:    {len(audit_results['corrupted'])}")
    print(f"  Exact duplicates:   {len(audit_results['duplicates'])}")
    print(f"  Missing classes:    {audit_results['missing_classes']}")

    print("\n  Class Distribution (Clean & De-duplicated):")
    for cname, count in sorted(audit_results["class_counts"].items()):
        pct = (count / audit_results["total_valid_cleaned"] * 100) if audit_results["total_valid_cleaned"] > 0 else 0
        print(f"    - {cname:<30}: {count:>5} ({pct:5.2f}%)")

    pd_cfg = dataset_cfg["datasets"]["plantdoc"]
    pd_raw = root / pd_cfg["raw_path"]
    print(f"\n[2] Auditing External Evaluation Dataset: PlantDoc")
    print(f"Path: {pd_raw}")

    plantdoc_records = []
    plantdoc_uncertain = []
    plantdoc_corrupted = []

    for split in ["train", "test"]:
        split_dir = pd_raw / split
        if not split_dir.exists():
            continue
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            folder_name = class_dir.name
            if "tomato" not in folder_name.lower():
                continue

            taxonomy_entry = PLANTDOC_TOMATO_TAXONOMY.get(folder_name)
            if not taxonomy_entry:
                continue

            for img_path in sorted(class_dir.iterdir()):
                if not img_path.is_file() or img_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                is_valid, err, dims, mode = inspect_image(img_path)
                if not is_valid:
                    plantdoc_corrupted.append({
                        "file_path": str(img_path),
                        "folder": folder_name,
                        "error": err,
                    })
                    continue

                rec = {
                    "file_path": str(img_path),
                    "relative_path": str(img_path.relative_to(root)),
                    "filename": img_path.name,
                    "original_split": split,
                    "folder_name": folder_name,
                    "class_id": taxonomy_entry["id"],
                    "class_name": taxonomy_entry["name"],
                    "status": taxonomy_entry["status"],
                    "sha256": compute_sha256(img_path),
                    "width": dims[0] if dims else 0,
                    "height": dims[1] if dims else 0,
                }

                if taxonomy_entry["status"] == "confirmed":
                    plantdoc_records.append(rec)
                else:
                    plantdoc_uncertain.append(rec)

    print(f"  PlantDoc confirmed evaluation images: {len(plantdoc_records)}")
    print(f"  PlantDoc uncertain / excluded images: {len(plantdoc_uncertain)}")
    print(f"  PlantDoc corrupted images:            {len(plantdoc_corrupted)}")

    pv_meta_file = metadata_dir / "plantvillage_metadata.json"
    with open(pv_meta_file, "w", encoding="utf-8") as f:
        json.dump(audit_results["records"], f, indent=2)

    pd_meta_file = metadata_dir / "plantdoc_metadata.json"
    with open(pd_meta_file, "w", encoding="utf-8") as f:
        json.dump({"confirmed": plantdoc_records, "uncertain_or_excluded": plantdoc_uncertain}, f, indent=2)

    dist_csv = output_audit_dir / "class_distribution.csv"
    with open(dist_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["class_id", "class_name", "plantvillage_clean_count", "share_pct"])
        for folder, meta in PLANTVILLAGE_TOMATO_TAXONOMY.items():
            cnt = audit_results["class_counts"].get(meta["name"], 0)
            pct = (cnt / audit_results["total_valid_cleaned"] * 100) if audit_results["total_valid_cleaned"] > 0 else 0
            writer.writerow([meta["id"], meta["name"], cnt, f"{pct:.2f}%"])

    corr_csv = output_audit_dir / "corrupted_images.csv"
    with open(corr_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "class_name", "file_path", "error_message"])
        for c in audit_results["corrupted"]:
            writer.writerow(["plantvillage", c["class_name"], c["file_path"], c["error"]])
        for c in plantdoc_corrupted:
            writer.writerow(["plantdoc", c["folder"], c["file_path"], c["error"]])

    dup_csv = output_audit_dir / "duplicate_report.csv"
    with open(dup_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sha256", "original_file", "duplicate_file", "class_name"])
        for d in audit_results["duplicates"]:
            writer.writerow([d["sha256"], d["original_path"], d["file_path"], d["class_name"]])

    inv_md = output_audit_dir / "dataset_inventory.md"
    with open(inv_md, "w", encoding="utf-8") as f:
        f.write("# AGRI-X Phase 2 Dataset Audit & Inventory Report\n\n")
        f.write(f"**PlantVillage Cleaned Images:** {audit_results['total_valid_cleaned']}\n\n")
        f.write(f"**PlantVillage Corrupted Count:** {len(audit_results['corrupted'])}\n\n")
        f.write(f"**PlantVillage Exact Duplicates Removed:** {len(audit_results['duplicates'])}\n\n")
        f.write(f"**PlantDoc Confirmed Evaluation Images:** {len(plantdoc_records)}\n\n")
        f.write(f"**PlantDoc Excluded / Ambiguous Images:** {len(plantdoc_uncertain)}\n\n")
        f.write("## PlantVillage Class Distribution\n")
        f.write("| ID | Class Name | Valid Count | Share |\n|---|---|---|---|\n")
        for folder, meta in PLANTVILLAGE_TOMATO_TAXONOMY.items():
            cnt = audit_results["class_counts"].get(meta["name"], 0)
            pct = (cnt / audit_results["total_valid_cleaned"] * 100) if audit_results["total_valid_cleaned"] > 0 else 0
            f.write(f"| {meta['id']} | `{meta['name']}` | {cnt} | {pct:.2f}% |\n")
        f.write("\n## PlantDoc External Evaluation Summary\n")
        f.write("| Folder Name | Mapped Class | Status | Count |\n|---|---|---|---|\n")
        pd_status_counts = {}
        for r in plantdoc_records + plantdoc_uncertain:
            k = (r["folder_name"], r["class_name"], r["status"])
            pd_status_counts[k] = pd_status_counts.get(k, 0) + 1
        for (folder, cname, status), cnt in sorted(pd_status_counts.items()):
            f.write(f"| `{folder}` | {cname} | `{status}` | {cnt} |\n")

    print("\n[Audit Pipeline Completed Successfully]")
    print(f"Generated reports in: {output_audit_dir}")
    print(f"Generated metadata in: {metadata_dir}")

if __name__ == "__main__":
    run()
