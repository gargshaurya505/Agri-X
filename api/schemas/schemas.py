"""Pydantic validation schemas for AGRI-X API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status (e.g., 'healthy', 'degraded')")
    model_loaded: bool = Field(..., description="Whether the neural network model is loaded into memory")
    model_architecture: str = Field(..., description="Model architecture name")
    num_classes: int = Field(..., description="Number of recognized disease classes")
    device: str = Field(..., description="Active compute device (mps, cuda, cpu)")
    gradcam_available: bool = Field(..., description="Whether Grad-CAM explanation service is initialized")


class ClassProbability(BaseModel):
    class_id: int
    class_name: str
    display_name: str
    probability: float = Field(..., description="Softmax confidence score as a percentage [0, 100]")


class PredictionResponse(BaseModel):
    prediction_id: str
    predicted_class: str
    display_name: str
    confidence: float = Field(..., description="Softmax confidence percentage [0, 100]")
    top_predictions: List[ClassProbability]
    model_name: str
    device: str
    explanation_available: bool = True


class ExplanationResponse(BaseModel):
    prediction_id: Optional[str] = None
    predicted_class: str
    display_name: str
    target_class: str
    confidence: float
    heatmap: str = Field(..., description="Data URL (data:image/png;base64,...) of normalized heatmap")
    overlay: str = Field(..., description="Data URL (data:image/png;base64,...) of blended Grad-CAM overlay")
    explanation_method: str = "Grad-CAM (layer4[-1])"
