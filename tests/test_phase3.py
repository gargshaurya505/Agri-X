"""Unit tests for Phase 3: Grad-CAM Explainability & Interpretability."""

import sys
from pathlib import Path
import pytest
import numpy as np
import torch
import torch.nn as nn
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.resnet18 import build_model
from src.explainability.grad_cam import GradCAM
from src.explainability.heatmap import resize_heatmap, colorize_heatmap, overlay_heatmap
from src.explainability.explanation_service import ExplanationService


class SyntheticConvNet(nn.Module):
    """Small synthetic CNN for fast unit testing."""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.target_conv = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(32, 5)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.target_conv(x))
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def test_gradcam_output_dimensions_and_normalization():
    """Verify Grad-CAM produces a 2D map with values strictly bounded in [0, 1]."""
    model = SyntheticConvNet()
    target_layer = model.target_conv
    grad_cam = GradCAM(model, target_layer)

    dummy_input = torch.randn(1, 3, 32, 32)
    cam, target_id, conf, logits = grad_cam.generate(dummy_input)

    assert cam.ndim == 2
    assert cam.shape == (32, 32)
    assert cam.min() >= 0.0
    assert cam.max() <= 1.0 + 1e-6
    assert 0 <= target_id < 5
    assert 0.0 <= conf <= 1.0

    grad_cam.remove_hooks()


def test_gradcam_custom_target_class():
    """Verify Grad-CAM generates explanations for user-specified target classes."""
    model = SyntheticConvNet()
    target_layer = model.target_conv
    grad_cam = GradCAM(model, target_layer)

    dummy_input = torch.randn(1, 3, 32, 32)
    cam, target_id, _, _ = grad_cam.generate(dummy_input, target_class=3)

    assert target_id == 3
    grad_cam.remove_hooks()


def test_weights_remain_unchanged_after_gradcam():
    """Verify that generating explanations does not mutate model weights."""
    model = SyntheticConvNet()
    grad_cam = GradCAM(model, model.target_conv)

    initial_fc_weight = model.fc.weight.clone()
    initial_conv_weight = model.target_conv.weight.clone()

    dummy_input = torch.randn(1, 3, 32, 32)
    _ = grad_cam.generate(dummy_input)

    assert torch.equal(model.fc.weight, initial_fc_weight)
    assert torch.equal(model.target_conv.weight, initial_conv_weight)

    grad_cam.remove_hooks()


def test_heatmap_resizing_and_colorization():
    """Verify heatmap resizing to target aspect ratios and 3-channel colorization."""
    raw_cam = np.random.rand(7, 7).astype(np.float32)
    resized = resize_heatmap(raw_cam, (256, 128))

    assert resized.shape == (128, 256)
    assert resized.dtype == np.float32

    colored = colorize_heatmap(resized, colormap_name="jet")
    assert colored.shape == (128, 256, 3)
    assert colored.dtype == np.uint8


def test_overlay_heatmap():
    """Verify overlay blending produces valid RGB PIL Image."""
    orig_img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    raw_cam = np.random.rand(10, 10).astype(np.float32)

    overlay = overlay_heatmap(orig_img, raw_cam, alpha=0.5)
    assert overlay.size == (200, 200)
    assert overlay.mode == "RGB"


def test_explanation_service_with_resnet18(tmp_path: Path):
    """Verify high-level ExplanationService pipeline end-to-end."""
    model = build_model(num_classes=10, pretrained=False)
    class_mapping = {i: f"Disease_{i}" for i in range(10)}
    service = ExplanationService(model=model, class_mapping=class_mapping, device=torch.device("cpu"))

    test_img_path = tmp_path / "leaf.jpg"
    test_img = Image.new("RGB", (224, 224), color=(30, 180, 50))
    test_img.save(test_img_path)

    result = service.explain_image(test_img_path)

    assert result.predicted_class_id in range(10)
    assert len(result.top_k_predictions) == 4
    assert result.overlay_image.size == (224, 224)
    assert result.raw_cam.shape == (224, 224)

    panel_file = tmp_path / "panel.png"
    service.save_explanation_panel(result, panel_file)
    assert panel_file.exists()
