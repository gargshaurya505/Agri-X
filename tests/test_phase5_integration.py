"""End-to-end integration and API tests for AGRI-X."""

import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app
from api.services.model_service import container


@pytest.fixture(scope="session", autouse=True)
def init_model():
    """Ensure model container is loaded."""
    if not container.is_loaded:
        container.load()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    """TEST 1: Health endpoint returns status, architecture, and device."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_architecture"] == "resnet18"
    assert data["num_classes"] == 10
    assert data["gradcam_available"] is True


def test_real_prediction_endpoint(client):
    """TEST 2, 3, 4: Real leaf prediction and top 5 probabilities."""
    sample_img_path = PROJECT_ROOT / "data/raw/plantvillage/raw/color/Tomato___Bacterial_spot/3e4ca861-5f1d-43c1-9b31-225455da4533___GCREC_Bact.Sp 3098.JPG"
    assert sample_img_path.exists(), "Sample test image not found"

    with open(sample_img_path, "rb") as f:
        img_bytes = f.read()

    response = client.post(
        "/api/v1/predict",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["predicted_class"] == "Bacterial Spot"
    assert data["display_name"] == "Bacterial Spot"
    assert data["confidence"] > 90.0
    assert len(data["top_predictions"]) == 5
    assert data["top_predictions"][0]["class_name"] == "Bacterial Spot"


def test_real_explain_endpoint(client):
    """TEST 5, 6: Real Grad-CAM heatmap and overlay generation."""
    sample_img_path = PROJECT_ROOT / "data/raw/plantvillage/raw/color/Tomato___Bacterial_spot/3e4ca861-5f1d-43c1-9b31-225455da4533___GCREC_Bact.Sp 3098.JPG"

    with open(sample_img_path, "rb") as f:
        img_bytes = f.read()

    response = client.post(
        "/api/v1/explain",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["predicted_class"] == "Bacterial Spot"
    assert data["target_class"] == "Bacterial Spot"
    assert data["heatmap"].startswith("data:image/png;base64,")
    assert data["overlay"].startswith("data:image/png;base64,")
    assert data["explanation_method"] == "Grad-CAM (layer4[-1])"


def test_empty_image_rejection(client):
    """TEST: Reject empty file."""
    response = client.post(
        "/api/v1/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_corrupted_image_rejection(client):
    """TEST: Reject unreadable corrupted file."""
    response = client.post(
        "/api/v1/predict",
        files={"file": ("corrupt.jpg", b"fake binary data not an image", "image/jpeg")}
    )
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower() or "corrupted" in response.json()["detail"].lower()


def test_healthy_leaf_inference(client):
    """TEST: Predict healthy tomato leaf."""
    sample_healthy = list((PROJECT_ROOT / "data/raw/plantvillage/raw/color/Tomato___healthy").glob("*.JPG"))[0]
    with open(sample_healthy, "rb") as f:
        img_bytes = f.read()

    response = client.post(
        "/api/v1/predict",
        files={"file": ("healthy.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_class"] == "Healthy"
    assert data["confidence"] > 80.0
