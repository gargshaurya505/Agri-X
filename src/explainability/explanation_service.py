"""High-level Explanation Service and visualizations for AGRI-X.

Orchestrates:
- Model forward & backward Grad-CAM attribution
- Original, Grayscale Heatmap, Color Heatmap, and Overlay generation
- Top-k prediction probability bar chart generation
- Side-by-side diagnostic panel creation
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from src.explainability.grad_cam import GradCAM
from src.explainability.heatmap import resize_heatmap, colorize_heatmap, overlay_heatmap
from src.data.dataset import get_transforms


@dataclass
class ExplanationResult:
    """Structured container for Grad-CAM explanation outputs."""
    image_path: str
    original_image: Image.Image
    predicted_class_id: int
    predicted_class_name: str
    target_class_id: int
    target_class_name: str
    confidence: float
    top_k_predictions: List[Dict[str, Any]]
    raw_cam: np.ndarray
    color_cam: np.ndarray
    overlay_image: Image.Image
    original_size: tuple[int, int]


class ExplanationService:
    """Service for computing and formatting model explanations."""

    def __init__(
        self,
        model: nn.Module,
        class_mapping: Dict[int, str],
        device: torch.device,
        target_layer: Optional[nn.Module] = None,
        image_size: tuple[int, int] = (224, 224),
    ):
        self.model = model.to(device)
        self.model.eval()
        self.class_mapping = class_mapping
        self.device = device
        self.image_size = image_size
        self.transform = get_transforms("test", image_size=image_size)

        if target_layer is None:
            if hasattr(model, "backbone") and hasattr(model.backbone, "layer4"):
                self.target_layer = model.backbone.layer4[-1]
            elif hasattr(model, "layer4"):
                self.target_layer = model.layer4[-1]
            else:
                raise ValueError("Could not automatically locate layer4 in the model.")
        else:
            self.target_layer = target_layer

        self.grad_cam = GradCAM(self.model, self.target_layer)

    def explain_image(
        self,
        image_path: str | Path,
        target_class: Optional[int] = None,
        top_k: int = 4,
        alpha: float = 0.45,
    ) -> ExplanationResult:
        """Generate comprehensive explanation for an input image file."""
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found at {img_path}")

        with Image.open(img_path) as raw_img:
            original_image = raw_img.convert("RGB")

        orig_w, orig_h = original_image.size

        input_tensor = self.transform(original_image).unsqueeze(0).to(self.device)

        cam, exp_target_id, conf, logits = self.grad_cam.generate(
            input_tensor, target_class=target_class
        )

        probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
        pred_class_id = int(logits.argmax(dim=1).item())
        pred_class_name = self.class_mapping.get(pred_class_id, f"Class {pred_class_id}")
        target_class_name = self.class_mapping.get(exp_target_id, f"Class {exp_target_id}")

        top_indices = np.argsort(probs)[::-1][:top_k]
        top_k_list = [
            {
                "class_id": int(idx),
                "class_name": self.class_mapping.get(int(idx), f"Class {idx}"),
                "probability": float(probs[idx]),
                "percentage": float(probs[idx] * 100),
            }
            for idx in top_indices
        ]

        resized_cam = resize_heatmap(cam, (orig_w, orig_h))
        color_cam = colorize_heatmap(resized_cam, colormap_name="jet")
        overlay = overlay_heatmap(original_image, cam, alpha=alpha, colormap_name="jet")

        return ExplanationResult(
            image_path=str(img_path),
            original_image=original_image,
            predicted_class_id=pred_class_id,
            predicted_class_name=pred_class_name,
            target_class_id=exp_target_id,
            target_class_name=target_class_name,
            confidence=conf,
            top_k_predictions=top_k_list,
            raw_cam=resized_cam,
            color_cam=color_cam,
            overlay_image=overlay,
            original_size=(orig_w, orig_h),
        )

    def save_explanation_panel(
        self,
        result: ExplanationResult,
        output_file: str | Path,
        dpi: int = 300,
    ) -> Path:
        """Create and save a 4-panel publication visualization:
        1. Original leaf photograph
        2. Normalized grayscale Grad-CAM heatmap
        3. Color heatmap overlay
        4. Top-K classification confidence horizontal bar chart
        """
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        fig = plt.figure(figsize=(18, 5))
        gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.3])

        ax1 = fig.add_subplot(gs[0, 0])
        ax1.imshow(result.original_image)
        ax1.set_title("Original Leaf Photograph", fontsize=12, pad=8)
        ax1.axis("off")

        ax2 = fig.add_subplot(gs[0, 1])
        im2 = ax2.imshow(result.raw_cam, cmap="magma")
        ax2.set_title("Grad-CAM Activation Map", fontsize=12, pad=8)
        ax2.axis("off")
        plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

        ax3 = fig.add_subplot(gs[0, 2])
        ax3.imshow(result.overlay_image)
        ax3.set_title(f"Diagnostic Attribution Overlay\n({result.target_class_name})", fontsize=12, pad=8)
        ax3.axis("off")

        ax4 = fig.add_subplot(gs[0, 3])
        classes = [p["class_name"] for p in result.top_k_predictions][::-1]
        probs = [p["probability"] for p in result.top_k_predictions][::-1]
        percentages = [p["percentage"] for p in result.top_k_predictions][::-1]

        y_pos = np.arange(len(classes))
        bars = ax4.barh(y_pos, probs, color="#2563eb", height=0.55, alpha=0.85)
        bars[-1].set_color("#16a34a" if result.predicted_class_id == result.target_class_id else "#dc2626")

        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(classes, fontsize=10)
        ax4.set_xlim(0, 1.05)
        ax4.set_xlabel("Model Softmax Probability", fontsize=11)
        ax4.set_title("Top Alternative Class Scores", fontsize=12, pad=8)
        ax4.grid(axis="x", linestyle="--", alpha=0.5)

        for i, bar in enumerate(bars):
            val = percentages[i]
            ax4.text(
                bar.get_width() + 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%",
                va="center",
                fontsize=9,
                fontweight="bold",
            )

        plt.suptitle(
            f"AGRI-X Explainability: Predicted '{result.predicted_class_name}' ({result.confidence * 100:.1f}% Confidence)",
            fontsize=14,
            fontweight="bold",
            y=1.03,
        )
        plt.tight_layout()
        plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
        plt.close()

        return out_path
