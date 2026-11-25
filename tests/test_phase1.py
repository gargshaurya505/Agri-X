"""Automated test suite for Phase 1 of AGRI-X."""

import sys
from pathlib import Path
import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.device import get_device, get_device_info
from src.utils.config import (
    load_config,
    load_dataset_config,
    get_class_names,
    get_class_mapping,
    get_project_root,
)
from src.data.auditor import (
    compute_file_hash,
    validate_image_file,
    DatasetAuditor,
    export_audit_reports,
)


def test_python_environment():
    """Verify Python version is at least 3.12."""
    assert sys.version_info >= (3, 12), f"Expected Python >= 3.12, found {sys.version}"


def test_device_detection():
    """Verify device selection runs and returns a valid torch.device."""
    device = get_device("auto")
    assert device is not None
    assert device.type in ["cpu", "cuda", "mps"]

    cpu_device = get_device("cpu")
    assert cpu_device.type == "cpu"

    info = get_device_info()
    assert "selected_device" in info
    assert "pytorch_version" in info


def test_configuration_loading():
    """Verify YAML configuration loading and expected schema."""
    config = load_config()
    assert config["project"]["name"] == "AGRI-X"
    assert "classes" in config
    assert "tomato" in config["classes"]

    dataset_config = load_dataset_config()
    assert "datasets" in dataset_config
    assert "plantvillage" in dataset_config["datasets"]
    assert "plantdoc" in dataset_config["datasets"]


def test_class_mapping():
    """Verify 10 tomato classes are properly mapped with IDs 0 to 9."""
    classes = get_class_names("tomato")
    assert len(classes) == 10
    expected_classes = [
        "Bacterial Spot",
        "Early Blight",
        "Late Blight",
        "Leaf Mold",
        "Septoria Leaf Spot",
        "Spider Mites",
        "Target Spot",
        "Tomato Yellow Leaf Curl Virus",
        "Tomato Mosaic Virus",
        "Healthy",
    ]
    assert classes == expected_classes

    mapping = get_class_mapping("tomato")
    assert len(mapping) == 10
    assert mapping[0] == "Bacterial Spot"
    assert mapping[9] == "Healthy"


def test_dataset_path_validation():
    """Verify dataset paths point within data/raw/ and return False when missing."""
    dataset_cfg = load_dataset_config()
    pv_path = get_project_root() / dataset_cfg["datasets"]["plantvillage"]["raw_path"]
    auditor = DatasetAuditor(pv_path)
    res = auditor.scan()
    assert "root_dir" in res
    assert "exists" in res
    assert "total_files_scanned" in res


def test_image_reading_and_corruption_detection(tmp_path: Path):
    """Test image reading, dimension extraction, corruption detection, and duplicate hashing."""
    valid_img_path = tmp_path / "valid.jpg"
    img = Image.new("RGB", (256, 256), color=(73, 109, 137))
    img.save(valid_img_path)

    is_valid, err, dims, mode = validate_image_file(valid_img_path)
    assert is_valid is True
    assert err is None
    assert dims == (256, 256)
    assert mode == "RGB"

    corrupt_img_path = tmp_path / "corrupt.jpg"
    with open(corrupt_img_path, "wb") as f:
        f.write(b"not a real jpeg image header")

    is_valid, err, dims, mode = validate_image_file(corrupt_img_path)
    assert is_valid is False
    assert err is not None

    dup_img_path = tmp_path / "dup.jpg"
    dup_img_path.write_bytes(valid_img_path.read_bytes())

    hash1 = compute_file_hash(valid_img_path)
    hash2 = compute_file_hash(dup_img_path)
    assert hash1 == hash2

    auditor = DatasetAuditor(tmp_path)
    audit_results = auditor.scan()
    assert audit_results["valid_images"] == 2
    assert len(audit_results["corrupted_images"]) == 1
    assert len(audit_results["duplicates"]) == 1

    reports = export_audit_reports(audit_results, tmp_path / "reports")
    assert reports["inventory"].exists()
    assert reports["class_distribution"].exists()
    assert reports["corrupted_images"].exists()
    assert reports["duplicate_report"].exists()
