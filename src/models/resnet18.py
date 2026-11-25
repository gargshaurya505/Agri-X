"""ResNet18 Model architecture with fine-tuning support for AGRI-X."""

from __future__ import annotations

from typing import Dict, Any, Optional
import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights


class AgriResNet18(nn.Module):
    """ResNet18 backbone with modular classification head and staged unfreezing."""

    def __init__(
        self,
        num_classes: int = 10,
        pretrained: bool = True,
        dropout_rate: float = 0.2,
    ):
        super().__init__()
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        self.backbone = resnet18(weights=weights)
        in_features = self.backbone.fc.in_features

        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, num_classes),
        )
        self.num_classes = num_classes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def freeze_backbone(self):
        """Freeze all layers except final classification head."""
        for param in self.backbone.parameters():
            param.requires_grad = False
        for param in self.backbone.fc.parameters():
            param.requires_grad = True

    def unfreeze_layer4_and_head(self):
        """Unfreeze layer4 and classification head for fine-tuning."""
        for param in self.backbone.layer4.parameters():
            param.requires_grad = True
        for param in self.backbone.fc.parameters():
            param.requires_grad = True

    def unfreeze_all(self):
        """Unfreeze all layers in the network."""
        for param in self.backbone.parameters():
            param.requires_grad = True


def build_model(
    num_classes: int = 10,
    pretrained: bool = True,
    dropout_rate: float = 0.2,
) -> AgriResNet18:
    """Factory function for building the model."""
    return AgriResNet18(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
    )
