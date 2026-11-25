"""Heatmap resizing, colorization, and overlay routines for AGRI-X."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def resize_heatmap(heatmap: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    """Resize 2D heatmap [0, 1] to target image dimensions (width, height) using bilinear interpolation."""
    img = Image.fromarray((heatmap * 255).astype(np.uint8), mode="L")
    resized = img.resize(target_size, resample=Image.Resampling.BILINEAR)
    return np.array(resized, dtype=np.float32) / 255.0


def colorize_heatmap(
    heatmap: np.ndarray,
    colormap_name: str = "jet",
) -> np.ndarray:
    """Apply a matplotlib colormap to a 2D normalized heatmap [0, 1].

    Returns:
        RGB numpy array of shape (H, W, 3) with values in range [0, 255], uint8.
    """
    colormap = plt.get_cmap(colormap_name)
    colored = colormap(heatmap)
    rgb = (colored[:, :, :3] * 255).astype(np.uint8)
    return rgb


def overlay_heatmap(
    original_image: Image.Image | np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.5,
    colormap_name: str = "jet",
) -> Image.Image:
    """Overlay colorized Grad-CAM heatmap onto the original image.

    Args:
        original_image: PIL Image or RGB numpy array [0, 255].
        heatmap: 2D numpy array [0, 1] matching or differing in dimensions.
        alpha: Heatmap transparency weight (0.0 = original image only, 1.0 = heatmap only).
        colormap_name: Colormap name (default: 'jet').

    Returns:
        PIL.Image: Composite overlay image.
    """
    if isinstance(original_image, np.ndarray):
        orig_pil = Image.fromarray(original_image.astype(np.uint8)).convert("RGB")
    else:
        orig_pil = original_image.convert("RGB")

    width, height = orig_pil.size

    if heatmap.shape != (height, width):
        resized_cam = resize_heatmap(heatmap, (width, height))
    else:
        resized_cam = heatmap

    color_cam = colorize_heatmap(resized_cam, colormap_name=colormap_name)
    color_cam_pil = Image.fromarray(color_cam)

    overlay = Image.blend(orig_pil, color_cam_pil, alpha=alpha)
    return overlay
