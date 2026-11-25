"""Grad-CAM (Gradient-weighted Class Activation Mapping) implementation for AGRI-X.

Calculates visual attribution maps for convolutional neural networks:
1. Registers forward & backward hooks on the target convolutional layer.
2. Extracts activation maps during forward inference.
3. Computes gradients of the target class score with respect to feature maps.
4. Performs Global Average Pooling on gradients to calculate channel importance weights.
5. Computes the weighted combination of feature activations followed by ReLU.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class GradCAM:
    """Grad-CAM interpreter for PyTorch models."""

    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self._hooks = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self._hooks.append(self.target_layer.register_forward_hook(forward_hook))
        self._hooks.append(self.target_layer.register_full_backward_hook(backward_hook))

    def remove_hooks(self):
        """Clean up registered hooks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()

    def generate(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
    ) -> Tuple[np.ndarray, int, float, torch.Tensor]:
        """Generate Grad-CAM heatmap for an input tensor.

        Args:
            input_tensor: Tensor of shape (1, C, H, W) or (C, H, W).
            target_class: Target class ID for explanation. If None, uses argmax prediction.

        Returns:
            Tuple of (raw_cam_map (H, W), target_class_id, confidence, logits_tensor)
        """
        if input_tensor.dim() == 3:
            input_tensor = input_tensor.unsqueeze(0)

        if input_tensor.size(0) != 1:
            raise ValueError(f"GradCAM expects batch size of 1, got {input_tensor.size(0)}")

        self.model.eval()

        input_tensor.requires_grad_(True)
        logits = self.model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)

        predicted_class = int(logits.argmax(dim=1).item())
        confidence = float(probabilities[0, predicted_class].item())

        if target_class is None:
            explanation_target = predicted_class
        else:
            explanation_target = int(target_class)

        self.model.zero_grad()

        score = logits[0, explanation_target]
        score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Failed to capture activations or gradients during Grad-CAM execution.")

        if not torch.isfinite(self.gradients).all() or not torch.isfinite(self.activations).all():
            logger.warning("Non-finite values encountered in gradients or activations.")
            self.gradients = torch.nan_to_num(self.gradients, 0.0)
            self.activations = torch.nan_to_num(self.activations, 0.0)

        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)

        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)

        cam = torch.relu(cam)

        cam_np = cam.squeeze().cpu().numpy()

        cam_min, cam_max = cam_np.min(), cam_np.max()
        if cam_max - cam_min > 1e-8:
            cam_normalized = (cam_np - cam_min) / (cam_max - cam_min)
        else:
            cam_normalized = np.zeros_like(cam_np)

        return cam_normalized, explanation_target, confidence, logits.detach()

    def __del__(self):
        self.remove_hooks()
