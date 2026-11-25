"""Configuration loader and validator for AGRI-X."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import yaml


def get_project_root() -> Path:
    """Return the absolute path of the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def load_yaml(path: str | Path) -> Dict[str, Any]:
    """Safely load and parse a YAML file."""
    path_obj = Path(path)
    if not path_obj.is_absolute():
        path_obj = get_project_root() / path_obj
    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path_obj}")

    with open(path_obj, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_config() -> Dict[str, Any]:
    """Load core project configuration."""
    return load_yaml("configs/config.yaml")


def load_dataset_config() -> Dict[str, Any]:
    """Load dataset configuration."""
    return load_yaml("configs/dataset_config.yaml")


def get_class_names(crop: str = "tomato") -> list[str]:
    """Retrieve list of class names for a given crop."""
    config = load_config()
    classes = config.get("classes", {}).get(crop, [])
    return [c["name"] for c in classes]


def get_class_mapping(crop: str = "tomato") -> Dict[int, str]:
    """Retrieve id-to-name mapping for a crop."""
    config = load_config()
    classes = config.get("classes", {}).get(crop, [])
    return {c["id"]: c["name"] for c in classes}
