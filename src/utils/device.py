"""Device utility for AGRI-X.

Supports Apple Silicon MPS (Metal Performance Shaders), NVIDIA CUDA,
and graceful fallback to CPU.
"""

from __future__ import annotations

import logging
from typing import Dict, Any
import torch

logger = logging.getLogger(__name__)


def get_device(preferred: str = "auto") -> torch.device:
    """Select the best available computation device.

    Args:
        preferred: One of 'auto', 'mps', 'cuda', 'cpu'.

    Returns:
        torch.device: The selected PyTorch device.
    """
    preferred_lower = preferred.lower().strip()

    if preferred_lower == "cuda":
        if torch.cuda.is_available():
            return torch.device("cuda")
        logger.warning("CUDA requested but not available. Falling back to auto-selection.")
    elif preferred_lower == "mps":
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return torch.device("mps")
        logger.warning("MPS requested but not available. Falling back to auto-selection.")
    elif preferred_lower == "cpu":
        return torch.device("cpu")

    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return torch.device("mps")
    return torch.device("cpu")


def get_device_info() -> Dict[str, Any]:
    """Retrieve detailed hardware and backend execution diagnostic information."""
    device = get_device()
    info: Dict[str, Any] = {
        "selected_device": str(device),
        "device_type": device.type,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "mps_available": (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
            and torch.backends.mps.is_built()
        ),
        "pytorch_version": torch.__version__,
    }
    return info
