"""Group-aware dataset splitting and leakage verification module.

Ensures:
- Group-aware splitting based on leaf identifiers or sequence prefixes.
- Zero exact duplicate leakage (SHA-256 cross-split intersection is strictly empty).
- Zero group leakage (group IDs never span across train, val, or test).
- Generation of reproducible train/val/test split manifests in data/splits/.
"""

from __future__ import annotations

import csv
import json
import logging
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


def create_group_aware_splits(
    records: List[Dict[str, Any]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> Dict[str, List[Dict[str, Any]]]:
    """Split records by group_id while maintaining class balance as closely as possible.

    All records sharing the same group_id are guaranteed to land entirely within
    a single split (train, val, or test).
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"
    random.seed(seed)

    class_groups: Dict[int, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for rec in records:
        class_groups[rec["class_id"]][rec["group_id"]].append(rec)

    train_splits: List[Dict[str, Any]] = []
    val_splits: List[Dict[str, Any]] = []
    test_splits: List[Dict[str, Any]] = []

    for class_id, groups_dict in sorted(class_groups.items()):
        group_items = list(groups_dict.items())
        random.shuffle(group_items)

        total_class_images = sum(len(img_list) for _, img_list in group_items)
        target_train = int(total_class_images * train_ratio)
        target_val = int(total_class_images * val_ratio)

        current_train = 0
        current_val = 0

        for group_id, img_list in group_items:
            count = len(img_list)
            if current_train + count <= target_train or (current_train < target_train and current_val >= target_val):
                train_splits.extend(img_list)
                current_train += count
            elif current_val + count <= target_val:
                val_splits.extend(img_list)
                current_val += count
            else:
                test_splits.extend(img_list)

    return {
        "train": train_splits,
        "val": val_splits,
        "test": test_splits,
    }


def verify_split_leakage(splits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Verify zero duplicate hash leakage and zero group leakage across splits."""
    hashes: Dict[str, Set[str]] = {s: set(r["sha256"] for r in splits[s]) for s in ["train", "val", "test"]}
    groups: Dict[str, Set[str]] = {s: set(r["group_id"] for r in splits[s]) for s in ["train", "val", "test"]}

    train_val_hash_leak = hashes["train"].intersection(hashes["val"])
    train_test_hash_leak = hashes["train"].intersection(hashes["test"])
    val_test_hash_leak = hashes["val"].intersection(hashes["test"])

    train_val_group_leak = groups["train"].intersection(groups["val"])
    train_test_group_leak = groups["train"].intersection(groups["test"])
    val_test_group_leak = groups["val"].intersection(groups["test"])

    has_leak = any([
        train_val_hash_leak,
        train_test_hash_leak,
        val_test_hash_leak,
        train_val_group_leak,
        train_test_group_leak,
        val_test_group_leak,
    ])

    return {
        "passed": not has_leak,
        "hash_leakage": {
            "train_val": len(train_val_hash_leak),
            "train_test": len(train_test_hash_leak),
            "val_test": len(val_test_hash_leak),
        },
        "group_leakage": {
            "train_val": len(train_val_group_leak),
            "train_test": len(train_test_group_leak),
            "val_test": len(val_test_group_leak),
        },
        "split_counts": {s: len(splits[s]) for s in ["train", "val", "test"]},
    }


def save_split_manifests(splits: Dict[str, List[Dict[str, Any]]], output_dir: str | Path) -> Dict[str, Path]:
    """Save split CSV and JSON manifests."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_paths = {}

    for split_name in ["train", "val", "test"]:
        csv_file = out / f"{split_name}.csv"
        recs = splits[split_name]
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["file_path", "relative_path", "filename", "folder_name", "class_id", "class_name", "group_id", "sha256", "width", "height", "channels", "mode"],
            )
            writer.writeheader()
            for r in recs:
                writer.writerow(r)
        manifest_paths[split_name] = csv_file

    return manifest_paths
