"""Comprehensive test suite for Phase 1 & 2 of AGRI-X.

Tests:
- Python environment & device selection
- Configuration loading & class taxonomy
- Dataset auditing, hash detection & corrupt image handling
- Group-aware split generation & zero-leakage enforcement
- Dataset class, DataLoader & image transform tensor outputs
- ResNet18 architecture forward pass, head freezing, layer4 unfreezing
- Checkpoint saving and round-trip state loading
- Metric calculations (Accuracy, Macro F1, Precision, Recall)
"""

import json
import sys
from pathlib import Path
import pytest
import torch
import torch.nn as nn
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
from src.data.preparation import (
    compute_sha256,
    inspect_image,
    PlantVillagePreparator,
)
from src.data.splitting import (
    create_group_aware_splits,
    verify_split_leakage,
)
from src.data.dataset import AgriLeafDataset, get_transforms
from src.models.resnet18 import build_model, AgriResNet18
from src.evaluation.evaluator import evaluate_model


def test_python_environment():
    """Verify Python version >= 3.12."""
    assert sys.version_info >= (3, 12)


def test_device_selection():
    """Verify hardware device selector."""
    dev = get_device("auto")
    assert dev.type in ["cpu", "cuda", "mps"]
    info = get_device_info()
    assert "selected_device" in info


def test_configuration_loading():
    """Verify YAML configuration."""
    cfg = load_config()
    assert cfg["project"]["name"] == "AGRI-X"
    assert len(cfg["classes"]["tomato"]) == 10
    d_cfg = load_dataset_config()
    assert "plantvillage" in d_cfg["datasets"]
    assert "plantdoc" in d_cfg["datasets"]


def test_class_mapping():
    """Verify 10 tomato classes."""
    classes = get_class_names("tomato")
    assert len(classes) == 10
    mapping = get_class_mapping("tomato")
    assert mapping[0] == "Bacterial Spot"
    assert mapping[9] == "Healthy"


def test_image_inspection_and_hashing(tmp_path: Path):
    """Test image reading, invalid file detection, and sha256 hashing."""
    valid_file = tmp_path / "valid.jpg"
    img = Image.new("RGB", (100, 100), color=(120, 200, 80))
    img.save(valid_file)

    is_valid, err, dims, mode = inspect_image(valid_file)
    assert is_valid is True
    assert dims == (100, 100)
    assert mode == "RGB"

    corrupted_file = tmp_path / "corrupted.jpg"
    corrupted_file.write_bytes(b"corrupted binary data")
    is_valid_c, err_c, dims_c, mode_c = inspect_image(corrupted_file)
    assert is_valid_c is False

    h1 = compute_sha256(valid_file)
    dup_file = tmp_path / "dup.jpg"
    dup_file.write_bytes(valid_file.read_bytes())
    h2 = compute_sha256(dup_file)
    assert h1 == h2


def test_group_aware_splitting_and_leakage_verification():
    """Test group-aware partitioning guarantees zero duplicate and zero group leakage."""
    records = []
    for c_id in range(3):
        for g_idx in range(5):
            group_id = f"group_c{c_id}_g{g_idx}"
            for img_idx in range(2):
                records.append({
                    "file_path": f"/dummy/{group_id}_{img_idx}.jpg",
                    "class_id": c_id,
                    "class_name": f"Class_{c_id}",
                    "group_id": group_id,
                    "sha256": f"hash_{group_id}_{img_idx}",
                })

    splits = create_group_aware_splits(records, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=42)
    assert len(splits["train"]) + len(splits["val"]) + len(splits["test"]) == len(records)

    leakage = verify_split_leakage(splits)
    assert leakage["passed"] is True
    assert leakage["hash_leakage"]["train_val"] == 0
    assert leakage["group_leakage"]["train_test"] == 0


def test_transforms_and_dataset(tmp_path: Path):
    """Verify PyTorch transforms and AgriLeafDataset tensor dimensions."""
    sample_file = tmp_path / "sample.jpg"
    img = Image.new("RGB", (300, 200), color=(50, 150, 250))
    img.save(sample_file)

    records = [{
        "file_path": str(sample_file),
        "class_id": 1,
        "class_name": "Early Blight",
        "sha256": "sample_hash",
        "group_id": "group_1",
    }]

    t_train = get_transforms("train", image_size=(224, 224))
    t_test = get_transforms("test", image_size=(224, 224))

    ds_train = AgriLeafDataset(records, transform=t_train)
    ds_test = AgriLeafDataset(records, transform=t_test)

    tensor_train, target_train, path_train = ds_train[0]
    tensor_test, target_test, path_test = ds_test[0]

    assert tensor_train.shape == (3, 224, 224)
    assert tensor_test.shape == (3, 224, 224)
    assert target_train == 1
    assert target_test == 1


def test_resnet18_model_and_checkpoint_roundtrip(tmp_path: Path):
    """Verify model creation, head replacement, and checkpoint save/load."""
    model = build_model(num_classes=10, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    out = model(x)
    assert out.shape == (2, 10)

    model.freeze_backbone()
    assert model.backbone.conv1.weight.requires_grad is False
    assert model.backbone.fc[1].weight.requires_grad is True

    model.unfreeze_layer4_and_head()
    assert model.backbone.layer4[0].conv1.weight.requires_grad is True

    ckpt_file = tmp_path / "test_model.pth"
    torch.save({
        "model_architecture": "resnet18",
        "num_classes": 10,
        "class_mapping": {i: f"Class_{i}" for i in range(10)},
        "model_state_dict": model.state_dict(),
    }, ckpt_file)

    model.eval()
    with torch.no_grad():
        out_eval = model(x)

    loaded_ckpt = torch.load(ckpt_file, map_location="cpu")
    model_reloaded = build_model(num_classes=loaded_ckpt["num_classes"], pretrained=False)
    model_reloaded.load_state_dict(loaded_ckpt["model_state_dict"])
    model_reloaded.eval()
    with torch.no_grad():
        out_reloaded = model_reloaded(x)

    assert torch.allclose(out_eval, out_reloaded, atol=1e-5)


def test_metric_calculations():
    """Verify classification evaluation metrics output format."""
    class DummyModel(nn.Module):
        def forward(self, x):
            b = x.size(0)
            logits = torch.zeros(b, 3)
            logits[:, 0] = 5.0
            return logits

    records = [
        {"file_path": "/dummy/1.jpg", "class_id": 0, "class_name": "C0"},
        {"file_path": "/dummy/2.jpg", "class_id": 1, "class_name": "C1"},
    ]

    class MockDataset(torch.utils.data.Dataset):
        def __len__(self):
            return 2
        def __getitem__(self, idx):
            return torch.zeros(3, 224, 224), records[idx]["class_id"], records[idx]["file_path"]

    loader = torch.utils.data.DataLoader(MockDataset(), batch_size=2)
    mapping = {0: "C0", 1: "C1", 2: "C2"}
    results = evaluate_model(DummyModel(), loader, torch.device("cpu"), mapping)

    assert "overall_metrics" in results
    assert results["overall_metrics"]["accuracy"] == 0.5
    assert len(results["misclassified"]) == 1
