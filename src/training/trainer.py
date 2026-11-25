"""Training engine with validation macro F1 checkpointing for AGRI-X."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

from src.utils.device import get_device

logger = logging.getLogger(__name__)


class AgriTrainer:
    """Trainer implementing training, validation, early stopping, and checkpointing."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: torch.utils.data.DataLoader,
        class_mapping: Dict[int, str],
        device: Optional[torch.device] = None,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        checkpoint_dir: str | Path = "models",
        experiment_dir: str | Path = "experiments",
    ):
        self.device = device or get_device()
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.class_mapping = class_mapping
        self.num_classes = len(class_mapping)

        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.experiment_dir = Path(experiment_dir)
        self.experiment_dir.mkdir(parents=True, exist_ok=True)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=learning_rate,
            weight_decay=weight_decay,
        )
        self.scheduler = ReduceLROnPlateau(
            self.optimizer, mode="max", factor=0.5, patience=2
        )

        self.history: List[Dict[str, Any]] = []
        self.best_macro_f1 = 0.0

    def set_optimizer_params(self, lr: float, weight_decay: float = 1e-4):
        """Update optimizer when unfreezing layers."""
        self.optimizer = AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=lr,
            weight_decay=weight_decay,
        )
        self.scheduler = ReduceLROnPlateau(
            self.optimizer, mode="max", factor=0.5, patience=2
        )

    def train_epoch(self) -> Tuple[float, float]:
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, targets, _ in self.train_loader:
            images = images.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, targets)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)

        epoch_loss = running_loss / total if total > 0 else 0.0
        epoch_acc = correct / total if total > 0 else 0.0
        return epoch_loss, epoch_acc

    @torch.no_grad()
    def validate(self) -> Dict[str, float]:
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_targets = []

        for images, targets, _ in self.val_loader:
            images = images.to(self.device)
            targets = targets.to(self.device)

            outputs = self.model(images)
            loss = self.criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())

        total = len(all_targets)
        val_loss = running_loss / total if total > 0 else 0.0
        val_acc = accuracy_score(all_targets, all_preds)
        val_f1_macro = f1_score(all_targets, all_preds, average="macro", zero_division=0)
        val_prec_macro = precision_score(all_targets, all_preds, average="macro", zero_division=0)
        val_rec_macro = recall_score(all_targets, all_preds, average="macro", zero_division=0)

        return {
            "val_loss": float(val_loss),
            "val_accuracy": float(val_acc),
            "val_macro_f1": float(val_f1_macro),
            "val_macro_precision": float(val_prec_macro),
            "val_macro_recall": float(val_rec_macro),
        }

    def save_checkpoint(
        self,
        filename: str,
        epoch: int,
        val_macro_f1: float,
        training_config: Dict[str, Any],
    ) -> Path:
        """Save a complete, self-contained model checkpoint."""
        save_path = self.checkpoint_dir / filename
        checkpoint = {
            "model_architecture": "resnet18",
            "num_classes": self.num_classes,
            "class_mapping": self.class_mapping,
            "input_size": [224, 224],
            "normalization": {
                "mean": [0.485, 0.456, 0.406],
                "std": [0.229, 0.224, 0.225],
            },
            "epoch": epoch,
            "val_macro_f1": val_macro_f1,
            "model_state_dict": self.model.state_dict(),
            "training_config": training_config,
        }
        torch.save(checkpoint, save_path)
        return save_path

    def train(
        self,
        epochs_head: int = 2,
        epochs_finetune: int = 3,
        lr_head: float = 1e-3,
        lr_finetune: float = 1e-4,
        early_stopping_patience: int = 3,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Execute staged transfer learning: head warm-up followed by layer4 fine-tuning."""
        total_epochs = epochs_head + epochs_finetune
        patience_counter = 0

        logger.info(f"--- Stage 1: Training Head ({epochs_head} epochs) ---")
        if hasattr(self.model, "freeze_backbone"):
            self.model.freeze_backbone()
        self.set_optimizer_params(lr=lr_head)

        training_meta = {
            "epochs_head": epochs_head,
            "epochs_finetune": epochs_finetune,
            "lr_head": lr_head,
            "lr_finetune": lr_finetune,
            "seed": seed,
            "device": str(self.device),
        }

        current_epoch = 0
        for ep in range(1, epochs_head + 1):
            current_epoch = ep
            start_time = time.time()
            train_loss, train_acc = self.train_epoch()
            val_metrics = self.validate()
            elapsed = time.time() - start_time

            val_f1 = val_metrics["val_macro_f1"]
            self.scheduler.step(val_f1)
            lr = self.optimizer.param_groups[0]["lr"]

            rec = {
                "epoch": current_epoch,
                "stage": "head",
                "learning_rate": lr,
                "train_loss": train_loss,
                "train_accuracy": train_acc,
                **val_metrics,
                "elapsed_seconds": elapsed,
            }
            self.history.append(rec)
            print(f"Epoch {current_epoch:02d}/{total_epochs:02d} [Head] | Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | Val Loss: {val_metrics['val_loss']:.4f} Macro F1: {val_f1:.4f} | {elapsed:.1f}s")

            self.save_checkpoint("latest_resnet18.pth", current_epoch, val_f1, training_meta)
            if val_f1 > self.best_macro_f1:
                self.best_macro_f1 = val_f1
                self.save_checkpoint("best_resnet18.pth", current_epoch, val_f1, training_meta)
                patience_counter = 0
            else:
                patience_counter += 1

        if epochs_finetune > 0:
            logger.info(f"--- Stage 2: Fine-tuning layer4 + Head ({epochs_finetune} epochs) ---")
            if hasattr(self.model, "unfreeze_layer4_and_head"):
                self.model.unfreeze_layer4_and_head()
            self.set_optimizer_params(lr=lr_finetune)

            for ep in range(1, epochs_finetune + 1):
                current_epoch += 1
                start_time = time.time()
                train_loss, train_acc = self.train_epoch()
                val_metrics = self.validate()
                elapsed = time.time() - start_time

                val_f1 = val_metrics["val_macro_f1"]
                self.scheduler.step(val_f1)
                lr = self.optimizer.param_groups[0]["lr"]

                rec = {
                    "epoch": current_epoch,
                    "stage": "finetune",
                    "learning_rate": lr,
                    "train_loss": train_loss,
                    "train_accuracy": train_acc,
                    **val_metrics,
                    "elapsed_seconds": elapsed,
                }
                self.history.append(rec)
                print(f"Epoch {current_epoch:02d}/{total_epochs:02d} [FineTune] | Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | Val Loss: {val_metrics['val_loss']:.4f} Macro F1: {val_f1:.4f} | {elapsed:.1f}s")

                self.save_checkpoint("latest_resnet18.pth", current_epoch, val_f1, training_meta)
                if val_f1 > self.best_macro_f1:
                    self.best_macro_f1 = val_f1
                    self.save_checkpoint("best_resnet18.pth", current_epoch, val_f1, training_meta)
                    patience_counter = 0
                else:
                    patience_counter += 1

                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping triggered at epoch {current_epoch}")
                    break

        history_file = self.experiment_dir / "training_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

        return {
            "best_macro_f1": self.best_macro_f1,
            "total_epochs_trained": current_epoch,
            "history": self.history,
        }
