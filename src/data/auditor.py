"""Dataset validation and auditing utilities for AGRI-X.

Implements raw image verification, corruption detection, duplicate hashing,
and audit reporting without altering original data files.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, UnidentifiedImageError

DEFAULT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def compute_file_hash(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute MD5 hash for exact duplicate detection."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_image_file(file_path: Path) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]], Optional[str]]:
    """Inspect and validate an image file.

    Returns:
        Tuple of (is_valid, error_message, (width, height), mode)
    """
    try:
        with Image.open(file_path) as img:
            img.verify()
        with Image.open(file_path) as img:
            dimensions = (img.width, img.height)
            mode = img.mode
            img.load()
        return True, None, dimensions, mode
    except (UnidentifiedImageError, OSError, ValueError) as e:
        return False, str(e), None, None


class DatasetAuditor:
    """Auditor for scanning image datasets, detecting corruptions and duplicates."""

    def __init__(self, root_dir: str | Path, supported_extensions: Optional[set[str]] = None):
        self.root_dir = Path(root_dir)
        self.extensions = supported_extensions or DEFAULT_EXTENSIONS

    def scan(self) -> Dict[str, Any]:
        """Perform a comprehensive audit of the dataset folder.

        Returns:
            Dictionary containing audit results and metrics.
        """
        results: Dict[str, Any] = {
            "root_dir": str(self.root_dir),
            "exists": self.root_dir.exists(),
            "total_files_scanned": 0,
            "valid_images": 0,
            "corrupted_images": [],
            "classes": {},
            "hashes": {},
            "duplicates": [],
            "dimensions_summary": {},
        }

        if not self.root_dir.exists():
            return results

        class_dirs = [d for d in self.root_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

        scan_targets = class_dirs if class_dirs else [self.root_dir]

        for target in sorted(scan_targets, key=lambda p: p.name):
            class_name = target.name if class_dirs else "uncategorized"
            class_images = 0

            for file_path in target.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.extensions:
                    results["total_files_scanned"] += 1
                    is_valid, err, dims, mode = validate_image_file(file_path)

                    if not is_valid:
                        results["corrupted_images"].append({
                            "class": class_name,
                            "path": str(file_path),
                            "error": err,
                        })
                        continue

                    results["valid_images"] += 1
                    class_images += 1

                    dim_key = f"{dims[0]}x{dims[1]}" if dims else "unknown"
                    results["dimensions_summary"][dim_key] = results["dimensions_summary"].get(dim_key, 0) + 1

                    file_hash = compute_file_hash(file_path)
                    if file_hash in results["hashes"]:
                        original_path = results["hashes"][file_hash]
                        results["duplicates"].append({
                            "hash": file_hash,
                            "original": original_path,
                            "duplicate": str(file_path),
                            "class": class_name,
                        })
                    else:
                        results["hashes"][file_hash] = str(file_path)

            results["classes"][class_name] = class_images

        return results


def export_audit_reports(audit_data: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    """Generate Markdown and CSV audit reports.

    Outputs:
        - dataset_inventory.md
        - class_distribution.csv
        - corrupted_images.csv
        - duplicate_report.csv
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    inv_path = out_path / "dataset_inventory.md"
    dist_path = out_path / "class_distribution.csv"
    corr_path = out_path / "corrupted_images.csv"
    dup_path = out_path / "duplicate_report.csv"

    with open(dist_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["class_name", "count", "percentage"])
        total_valid = audit_data.get("valid_images", 0)
        classes = audit_data.get("classes", {})
        for cname, count in sorted(classes.items()):
            pct = (count / total_valid * 100) if total_valid > 0 else 0.0
            writer.writerow([cname, count, f"{pct:.2f}%"])

    with open(corr_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["class_name", "file_path", "error_message"])
        for corr in audit_data.get("corrupted_images", []):
            writer.writerow([corr.get("class"), corr.get("path"), corr.get("error")])

    with open(dup_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["hash", "original_file", "duplicate_file", "class_name"])
        for dup in audit_data.get("duplicates", []):
            writer.writerow([dup.get("hash"), dup.get("original"), dup.get("duplicate"), dup.get("class")])

    exists = audit_data.get("exists", False)
    total_scanned = audit_data.get("total_files_scanned", 0)
    valid_count = audit_data.get("valid_images", 0)
    corr_count = len(audit_data.get("corrupted_images", []))
    dup_count = len(audit_data.get("duplicates", []))

    status_tag = "READY" if (exists and total_scanned > 0) else "PENDING DATASET PLACEMENT"

    md_content = f"""# AGRI-X Dataset Audit & Inventory Report

**Dataset Path:** `{audit_data.get('root_dir', 'Unknown')}`  
**Audit Status:** `{status_tag}`  
**Path Exists:** `{exists}`  

- **Total Files Scanned:** {total_scanned}
- **Valid Images:** {valid_count}
- **Corrupted / Unreadable Images:** {corr_count}
- **Exact Duplicates Detected:** {dup_count}

| Class Name | Image Count | Share |
|---|---|---|
"""
    if classes:
        for cname, count in sorted(classes.items()):
            pct = (count / valid_count * 100) if valid_count > 0 else 0.0
            md_content += f"| `{cname}` | {count} | {pct:.2f}% |\n"
    else:
        md_content += "| *No classes scanned (Datasets Pending)* | 0 | 0.00% |\n"

    md_content += "\n## Image Dimensions Summary\n"
    dim_summary = audit_data.get("dimensions_summary", {})
    if dim_summary:
        md_content += "| Resolution (WxH) | Count |\n|---|---|\n"
        for dim, count in sorted(dim_summary.items(), key=lambda x: x[1], reverse=True):
            md_content += f"| `{dim}` | {count} |\n"
    else:
        md_content += "*No image dimension data recorded.*\n"

    md_content += f"""
- Class Distribution CSV: [{dist_path.name}](./{dist_path.name})
- Corrupted Images Log: [{corr_path.name}](./{corr_path.name})
- Duplicate Detection Report: [{dup_path.name}](./{dup_path.name})
"""

    with open(inv_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "inventory": inv_path,
        "class_distribution": dist_path,
        "corrupted_images": corr_path,
        "duplicate_report": dup_path,
    }
