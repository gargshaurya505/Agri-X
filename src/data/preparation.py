"""Comprehensive Dataset Preparation and Auditing Module for AGRI-X.

Provides:
- Exact SHA-256 hash computation
- Image integrity checking (Pillow load + verify)
- PlantVillage leaf-group mapping extraction
- Detection of corrupted, unreadable, and exact duplicate images
- Non-destructive dataset cleaning and metadata generation
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

PLANTVILLAGE_TOMATO_TAXONOMY = {
    "Tomato___Bacterial_spot": {"id": 0, "name": "Bacterial Spot", "slug": "bacterial_spot"},
    "Tomato___Early_blight": {"id": 1, "name": "Early Blight", "slug": "early_blight"},
    "Tomato___Late_blight": {"id": 2, "name": "Late Blight", "slug": "late_blight"},
    "Tomato___Leaf_Mold": {"id": 3, "name": "Leaf Mold", "slug": "leaf_mold"},
    "Tomato___Septoria_leaf_spot": {"id": 4, "name": "Septoria Leaf Spot", "slug": "septoria_leaf_spot"},
    "Tomato___Spider_mites Two-spotted_spider_mite": {"id": 5, "name": "Spider Mites", "slug": "spider_mites"},
    "Tomato___Target_Spot": {"id": 6, "name": "Target Spot", "slug": "target_spot"},
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {"id": 7, "name": "Tomato Yellow Leaf Curl Virus", "slug": "yellow_leaf_curl_virus"},
    "Tomato___Tomato_mosaic_virus": {"id": 8, "name": "Tomato Mosaic Virus", "slug": "mosaic_virus"},
    "Tomato___healthy": {"id": 9, "name": "Healthy", "slug": "healthy"},
}

PLANTDOC_TOMATO_TAXONOMY = {
    "Tomato Early blight leaf": {"id": 1, "name": "Early Blight", "status": "confirmed"},
    "Tomato Septoria leaf spot": {"id": 4, "name": "Septoria Leaf Spot", "status": "confirmed"},
    "Tomato leaf bacterial spot": {"id": 0, "name": "Bacterial Spot", "status": "confirmed"},
    "Tomato leaf late blight": {"id": 2, "name": "Late Blight", "status": "confirmed"},
    "Tomato leaf mosaic virus": {"id": 8, "name": "Tomato Mosaic Virus", "status": "confirmed"},
    "Tomato leaf yellow virus": {"id": 7, "name": "Tomato Yellow Leaf Curl Virus", "status": "confirmed"},
    "Tomato mold leaf": {"id": 3, "name": "Leaf Mold", "status": "confirmed"},
    "Tomato two spotted spider mites leaf": {"id": 5, "name": "Spider Mites", "status": "insufficient_samples"},
    "Tomato leaf": {"id": None, "name": "Uncertain / Generic leaf", "status": "ambiguous_excluded"},
}


def compute_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash for strict duplicate detection."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect_image(file_path: Path) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]], Optional[str]]:
    """Strictly validate image file integrity and retrieve dimensions and mode."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        with Image.open(file_path) as img:
            dims = (img.width, img.height)
            mode = img.mode
            img.load()
        return True, None, dims, mode
    except (UnidentifiedImageError, OSError, ValueError) as e:
        return False, str(e), None, None


class PlantVillagePreparator:
    """Audits and builds clean metadata for PlantVillage tomato subset."""

    def __init__(self, raw_dir: str | Path, leaf_map_path: Optional[str | Path] = None):
        self.raw_dir = Path(raw_dir)
        self.leaf_map_path = Path(leaf_map_path) if leaf_map_path else None
        self.leaf_map: Dict[str, str] = {}
        if self.leaf_map_path and self.leaf_map_path.exists():
            self._load_leaf_map()

    def _load_leaf_map(self):
        try:
            with open(self.leaf_map_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for img_id, leaf_info in data.items():
                    if isinstance(leaf_info, list) and leaf_info:
                        self.leaf_map[img_id.strip()] = leaf_info[0]
                    elif isinstance(leaf_info, str):
                        self.leaf_map[img_id.strip()] = leaf_info
        except Exception as e:
            logger.warning(f"Failed to load leaf map: {e}")

    def get_group_id(self, file_path: Path, class_folder: str) -> str:
        """Derive leaf group ID from leaf-map.json or filename pattern."""
        stem = file_path.stem.strip()
        if stem in self.leaf_map:
            return f"leaf_{self.leaf_map[stem]}"
        for key, val in self.leaf_map.items():
            if key in stem or stem in key:
                return f"leaf_{val}"
        return f"group_{class_folder}_{stem}"

    def audit_and_prepare(self) -> Dict[str, Any]:
        """Audit dataset, detect duplicates, and compile records."""
        records: List[Dict[str, Any]] = []
        corrupted: List[Dict[str, Any]] = []
        duplicates: List[Dict[str, Any]] = []
        seen_hashes: Dict[str, str] = {}
        class_counts: Dict[str, int] = {}
        missing_classes: List[str] = []

        for folder_name, meta in PLANTVILLAGE_TOMATO_TAXONOMY.items():
            class_dir = self.raw_dir / folder_name
            if not class_dir.exists():
                missing_classes.append(folder_name)
                continue

            class_id = meta["id"]
            class_name = meta["name"]
            class_counts[class_name] = 0

            for img_path in sorted(class_dir.iterdir()):
                if not img_path.is_file() or img_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                is_valid, err, dims, mode = inspect_image(img_path)
                if not is_valid:
                    corrupted.append({
                        "file_path": str(img_path),
                        "folder": folder_name,
                        "class_name": class_name,
                        "error": err,
                    })
                    continue

                file_hash = compute_sha256(img_path)
                if file_hash in seen_hashes:
                    duplicates.append({
                        "file_path": str(img_path),
                        "original_path": seen_hashes[file_hash],
                        "sha256": file_hash,
                        "folder": folder_name,
                        "class_name": class_name,
                    })
                    continue

                seen_hashes[file_hash] = str(img_path)
                group_id = self.get_group_id(img_path, folder_name)

                record = {
                    "file_path": str(img_path),
                    "relative_path": str(img_path.relative_to(self.raw_dir.parent.parent.parent)),
                    "filename": img_path.name,
                    "folder_name": folder_name,
                    "class_id": class_id,
                    "class_name": class_name,
                    "sha256": file_hash,
                    "width": dims[0] if dims else 256,
                    "height": dims[1] if dims else 256,
                    "channels": 3 if mode == "RGB" else 1,
                    "mode": mode,
                    "group_id": group_id,
                }
                records.append(record)
                class_counts[class_name] += 1

        return {
            "records": records,
            "corrupted": corrupted,
            "duplicates": duplicates,
            "class_counts": class_counts,
            "missing_classes": missing_classes,
            "total_valid_cleaned": len(records),
        }
