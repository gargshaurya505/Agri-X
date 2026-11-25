#!/usr/bin/env python3
"""CLI script to train AGRI-X ResNet18 model."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.config import get_project_root, get_class_mapping
from src.utils.device import get_device, get_device_info
from src.data.dataset import get_data_loaders
from src.models.resnet18 import build_model
from src.training.trainer import AgriTrainer


def parse_args():
    parser = argparse.ArgumentParser(description="Train AGRI-X ResNet18 Model")
    parser.add_argument("--epochs-head", type=int, default=2, help="Epochs for training head")
    parser.add_argument("--epochs-finetune", type=int, default=3, help="Epochs for fine-tuning layer4+head")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr-head", type=float, default=1e-3, help="Learning rate for head")
    parser.add_argument("--lr-finetune", type=float, default=1e-4, help="Learning rate for fine-tuning")
    parser.add_argument("--num-workers", type=int, default=4, help="DataLoader workers")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def main():
    args = parse_args()
    root = get_project_root()
    splits_dir = root / "data" / "splits"
    models_dir = root / "models"
    experiments_dir = root / "experiments"

    print("=" * 70)
    print("AGRI-X RESNET18 TRAINING PIPELINE")
    print("=" * 70)

    device = get_device()
    dev_info = get_device_info()
    print(f"Selected Device: {device} (MPS available: {dev_info['mps_available']})")

    class_mapping = get_class_mapping("tomato")
    print(f"Loaded {len(class_mapping)} classes: {list(class_mapping.values())}")

    mapping_file = models_dir / "class_mapping.json"
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=2)

    train_cfg_file = models_dir / "training_config.json"
    with open(train_cfg_file, "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=2)

    print("\n[Loading Datasets & Creating DataLoaders]")
    loaders = get_data_loaders(
        splits_dir=splits_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
        seed=args.seed,
    )
    print(f"  Train samples: {len(loaders['train'].dataset)}")
    print(f"  Val samples:   {len(loaders['val'].dataset)}")
    print(f"  Test samples:  {len(loaders['test'].dataset)} (Kept untouched during training)")

    print("\n[Initializing ResNet18 Architecture]")
    model = build_model(num_classes=len(class_mapping), pretrained=True)

    trainer = AgriTrainer(
        model=model,
        train_loader=loaders["train"],
        val_loader=loaders["val"],
        class_mapping=class_mapping,
        device=device,
        checkpoint_dir=models_dir,
        experiment_dir=experiments_dir,
    )

    print("\n[Starting Staged Transfer Learning Training]")
    result = trainer.train(
        epochs_head=args.epochs_head,
        epochs_finetune=args.epochs_finetune,
        lr_head=args.lr_head,
        lr_finetune=args.lr_finetune,
        seed=args.seed,
    )

    print("\n" + "=" * 70)
    print(f"Training Complete! Best Validation Macro F1: {result['best_macro_f1']:.4f}")
    print(f"Model Checkpoints saved to: {models_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
