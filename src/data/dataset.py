"""PyTorch Dataset, transforms, and DataLoaders for AGRI-X."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms(
    split: str,
    image_size: tuple[int, int] = (224, 224),
    mean: list[float] = IMAGENET_MEAN,
    std: list[float] = IMAGENET_STD,
) -> transforms.Compose:
    """Configurable transforms with augmentation strictly isolated to training."""
    if split == "train":
        return transforms.Compose([
            transforms.Resize(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
    else:
        return transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])


class AgriLeafDataset(Dataset):
    """Dataset for loading leaf images from a split manifest or record list."""

    def __init__(
        self,
        manifest_path_or_records: str | Path | List[Dict[str, Any]],
        transform: Optional[Callable] = None,
        base_dir: Optional[str | Path] = None,
    ):
        self.transform = transform
        self.base_dir = Path(base_dir) if base_dir else None
        self.samples: List[Dict[str, Any]] = []

        if isinstance(manifest_path_or_records, (str, Path)):
            manifest_file = Path(manifest_path_or_records)
            if not manifest_file.exists():
                raise FileNotFoundError(f"Manifest file not found: {manifest_file}")
            with open(manifest_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.samples.append({
                        "file_path": row["file_path"],
                        "class_id": int(row["class_id"]),
                        "class_name": row["class_name"],
                        "sha256": row.get("sha256", ""),
                        "group_id": row.get("group_id", ""),
                    })
        else:
            self.samples = manifest_path_or_records

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        sample = self.samples[idx]
        img_path = Path(sample["file_path"])
        if not img_path.is_absolute() and self.base_dir:
            img_path = self.base_dir / img_path

        with Image.open(img_path) as img:
            image = img.convert("RGB")

        if self.transform:
            image = self.transform(image)

        class_id = sample["class_id"]
        return image, class_id, sample["file_path"]


def get_data_loaders(
    splits_dir: str | Path,
    batch_size: int = 64,
    num_workers: int = 4,
    pin_memory: bool = True,
    seed: int = 42,
) -> Dict[str, DataLoader]:
    """Create reproducible DataLoaders for train, val, and test splits."""
    splits_path = Path(splits_dir)

    train_ds = AgriLeafDataset(
        splits_path / "train.csv",
        transform=get_transforms("train"),
    )
    val_ds = AgriLeafDataset(
        splits_path / "val.csv",
        transform=get_transforms("val"),
    )
    test_ds = AgriLeafDataset(
        splits_path / "test.csv",
        transform=get_transforms("test"),
    )

    g = torch.Generator()
    g.manual_seed(seed)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        generator=g,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

    return {
        "train": train_loader,
        "val": val_loader,
        "test": test_loader,
    }
