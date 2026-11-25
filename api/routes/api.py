"""FastAPI route handlers for AGRI-X local AI service."""

from __future__ import annotations

import base64
import io
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image
import torch

from api.schemas.schemas import HealthResponse, PredictionResponse, ExplanationResponse, ClassProbability
from api.services.model_service import container, validate_image_bytes

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Verify local AI backend status, device, and model readiness."""
    return HealthResponse(
        status="healthy" if container.is_loaded else "model_unavailable",
        model_loaded=container.is_loaded,
        model_architecture=container.architecture,
        num_classes=container.num_classes,
        device=str(container.device) if container.device else "unknown",
        gradcam_available=(container.explanation_service is not None),
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
):
    """Run real ResNet18 neural inference on an uploaded tomato leaf photograph."""
    if not container.is_loaded or container.explanation_service is None:
        raise HTTPException(status_code=503, detail="Local AI model is not loaded.")

    contents = await file.read()
    try:
        rgb_image, _ = validate_image_bytes(contents, file.filename or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        service = container.explanation_service
        input_tensor = service.transform(rgb_image).unsqueeze(0).to(service.device)

        service.grad_cam.model.eval()
        with torch.no_grad():
            logits = service.grad_cam.model(input_tensor)
            probs = logits.softmax(dim=1).squeeze().detach().cpu().numpy()

        pred_id = int(logits.argmax(dim=1).item())
        pred_name = container.class_mapping.get(pred_id, f"Class {pred_id}")
        pred_confidence = float(probs[pred_id] * 100.0)

        top_indices = probs.argsort()[::-1][:5]
        top_preds = [
            ClassProbability(
                class_id=int(idx),
                class_name=container.class_mapping.get(int(idx), f"Class {idx}"),
                display_name=container.class_mapping.get(int(idx), f"Class {idx}"),
                probability=float(probs[idx] * 100.0),
            )
            for idx in top_indices
        ]

        return PredictionResponse(
            prediction_id=f"pred_{uuid.uuid4().hex[:12]}",
            predicted_class=pred_name,
            display_name=pred_name,
            confidence=pred_confidence,
            top_predictions=top_preds,
            model_name=container.architecture.upper(),
            device=str(container.device),
            explanation_available=True,
        )
    except Exception as e:
        logger.exception("Inference error occurred")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/explain", response_model=ExplanationResponse)
async def explain_disease(
    file: UploadFile = File(...),
    target_class: Optional[int] = Form(None),
):
    """Compute real Grad-CAM visual heatmaps and overlays using layer4[-1]."""
    if not container.is_loaded or container.explanation_service is None:
        raise HTTPException(status_code=503, detail="Local AI model is not loaded.")

    contents = await file.read()
    try:
        rgb_image, _ = validate_image_bytes(contents, file.filename or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        service = container.explanation_service
        orig_w, orig_h = rgb_image.size
        input_tensor = service.transform(rgb_image).unsqueeze(0).to(service.device)

        cam, exp_target_id, conf, logits = service.grad_cam.generate(
            input_tensor, target_class=target_class
        )

        pred_id = int(logits.argmax(dim=1).item())
        pred_name = container.class_mapping.get(pred_id, f"Class {pred_id}")
        target_name = container.class_mapping.get(exp_target_id, f"Class {exp_target_id}")

        from src.explainability.heatmap import resize_heatmap, colorize_heatmap, overlay_heatmap
        resized_cam = resize_heatmap(cam, (orig_w, orig_h))
        color_cam = colorize_heatmap(resized_cam, colormap_name="jet")
        overlay = overlay_heatmap(rgb_image, cam, alpha=0.45, colormap_name="jet")

        cam_buf = io.BytesIO()
        Image.fromarray(color_cam).save(cam_buf, format="PNG")
        cam_base64 = f"data:image/png;base64,{base64.b64encode(cam_buf.getvalue()).decode('utf-8')}"

        overlay_buf = io.BytesIO()
        overlay.save(overlay_buf, format="PNG")
        overlay_base64 = f"data:image/png;base64,{base64.b64encode(overlay_buf.getvalue()).decode('utf-8')}"

        return ExplanationResponse(
            prediction_id=f"exp_{uuid.uuid4().hex[:12]}",
            predicted_class=pred_name,
            display_name=pred_name,
            target_class=target_name,
            confidence=float(conf * 100.0),
            heatmap=cam_base64,
            overlay=overlay_base64,
            explanation_method="Grad-CAM (layer4[-1])",
        )
    except Exception as e:
        logger.exception("Grad-CAM generation error occurred")
        raise HTTPException(status_code=500, detail=f"Explainability error: {str(e)}")
