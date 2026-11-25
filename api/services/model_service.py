"""Global model singleton and lifecycle manager for AGRI-X local AI service."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import torch
import torch.nn as nn
from PIL import Image

from src.models.resnet18 import build_model
from src.explainability.explanation_service import ExplanationService
from src.utils.device import get_device, get_device_info
from src.utils.config import get_project_root

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}


class ModelContainer:
    """Manages model loading once at startup and services inference/Grad-CAM requests."""

    def __init__(self):
        self.model: Optional[nn.Module] = None
        self.explanation_service: Optional[ExplanationService] = None
        self.class_mapping: Dict[int, str] = {}
        self.num_classes: int = 0
        self.device: Optional[torch.device] = None
        self.architecture: str = "resnet18"
        self.is_loaded: bool = False

    def load(self, checkpoint_path: Optional[Path] = None):
        root = get_project_root()
        ckpt_file = checkpoint_path or (root / "models" / "best_resnet18.pth")

        if not ckpt_file.exists():
            raise FileNotFoundError(f"Model checkpoint not found at: {ckpt_file}")

        self.device = get_device()
        logger.info(f"Loading AGRI-X model on device: {self.device} from {ckpt_file}")

        checkpoint = torch.load(ckpt_file, map_location=self.device)
        self.num_classes = checkpoint["num_classes"]
        self.class_mapping = {int(k): v for k, v in checkpoint["class_mapping"].items()}
        self.architecture = checkpoint.get("model_architecture", "resnet18")

        self.model = build_model(num_classes=self.num_classes, pretrained=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

        self.explanation_service = ExplanationService(
            model=self.model,
            class_mapping=self.class_mapping,
            device=self.device,
        )

        self.is_loaded = True
        logger.info(f"Model successfully initialized with {self.num_classes} classes.")


container = ModelContainer()


def validate_image_bytes(image_bytes: bytes, filename: str = "") -> Tuple[Image.Image, str]:
    """Validate image bytes, enforce size limit, and return clean RGB PIL Image."""
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Uploaded file is empty.")

    if len(image_bytes) > MAX_FILE_SIZE:
        raise ValueError("File exceeds maximum upload size of 10 MB.")

    try:
        raw_stream = io.BytesIO(image_bytes)
        with Image.open(raw_stream) as img:
            img.verify()
            img_format = img.format or "JPEG"

        raw_stream.seek(0)
        with Image.open(raw_stream) as img:
            rgb_image = img.convert("RGB")
            rgb_image.load()

        return rgb_image, img_format
    except Exception as e:
        raise ValueError(f"Corrupted or invalid image file: {str(e)}")
