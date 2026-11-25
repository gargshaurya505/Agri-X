#!/usr/bin/env python3
"""Create reproducible group-aware train/val/test splits and verify zero leakage."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root
from src.data.splitting import (
    create_group_aware_splits,
    verify_split_leakage,
    save_split_manifests,
)


def run():
    root = get_project_root()
    metadata_file = root / "data" / "metadata" / "plantvillage_metadata.json"
    splits_dir = root / "data" / "splits"

    print("=" * 70)
    print("AGRI-X SPLIT GENERATION & LEAKAGE VERIFICATION")
    print("=" * 70)

    if not metadata_file.exists():
        print(f"Error: {metadata_file} not found. Run audit first.")
        sys.exit(1)

    with open(metadata_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Total cleaned records: {len(records)}")

    splits = create_group_aware_splits(
        records,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15,
        seed=42,
    )

    leakage_report = verify_split_leakage(splits)

    print("\n[Split Manifest Image Counts]")
    for s, cnt in leakage_report["split_counts"].items():
        pct = cnt / len(records) * 100
        print(f"  {s:<6}: {cnt:>5} ({pct:.2f}%)")

    print("\n[Leakage Verification Results]")
    print(f"  Passed (Zero Leakage): {leakage_report['passed']}")
    print(f"  Hash Cross-Overlap:    {leakage_report['hash_leakage']}")
    print(f"  Group Cross-Overlap:   {leakage_report['group_leakage']}")

    if not leakage_report["passed"]:
        print("ERROR: Data leakage detected across splits! Aborting.")
        sys.exit(1)

    manifest_paths = save_split_manifests(splits, splits_dir)
    print(f"\nManifests saved to:")
    for s, path in manifest_paths.items():
        print(f"  {s}: {path}")

    verification_file = root / "reports" / "dataset_audit" / "split_verification.json"
    with open(verification_file, "w", encoding="utf-8") as f:
        json.dump(leakage_report, f, indent=2)
    print(f"Verification report saved to: {verification_file}")


if __name__ == "__main__":
    run()
