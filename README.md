# AGRI-X – Explainable AI-Based Crop Disease Detection and Agricultural Intelligence System

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AGRI-X** is an end-to-end, explainable artificial intelligence system engineered to identify crop diseases, quantify classification uncertainty, generate visual heatmaps using Grad-CAM, provide actionable agricultural advisory, and maintain diagnostic histories for precision farming.

---

## 1. Project Objectives
- **Accurate Disease Classification**: Multi-class visual classification across crop pathologies, initialized on 10 tomato leaf categories.
- **Explainable Diagnostics (XAI)**: Visual attribution through Grad-CAM to confirm the model attends to pathological lesions rather than background artifacts.
- **Cross-Domain Generalization**: Stress-testing models trained on lab-conditioned benchmarks (PlantVillage) against in-the-wild photography (PlantDoc).
- **Extensible Architecture**: Modular foundation ready to accommodate multi-crop extensions, RESTful APIs, and responsive interactive web interfaces.

---

## 2. Supported Tomato Classes (Phase 1 Baseline)
1. **Bacterial Spot** (*Xanthomonas campestris pv. vesicatoria*)
2. **Early Blight** (*Alternaria solani*)
3. **Late Blight** (*Phytophthora infestans*)
4. **Leaf Mold** (*Passalora fulva*)
5. **Septoria Leaf Spot** (*Septoria lycopersici*)
6. **Spider Mites / Two-spotted spider mite** (*Tetranychus urticae*)
7. **Target Spot** (*Corynespora cassiicola*)
8. **Tomato Yellow Leaf Curl Virus (TYLCV)**
9. **Tomato Mosaic Virus (ToMV)**
10. **Healthy** (*Solanum lycopersicum*)

---

## 3. Technology Stack
- **Machine Learning & CV**: Python 3.12, PyTorch, Torchvision (ResNet18), NumPy, Pandas, Scikit-learn, PIL.
- **Visualization & Explainability**: Matplotlib, Seaborn, Grad-CAM (Target layer: `layer4`).
- **Backend API**: FastAPI, Pydantic, Uvicorn (Phase 4).
- **Database**: SQLite (Phase 4).
- **Frontend**: React, Vite, Tailwind CSS, Lucide React, Recharts (Phase 5).
- **Testing & Tooling**: Pytest, YAML, Tqdm.

---

## 4. Project Directory Structure
```text
AGRI-X/
│
├── api/                     # Backend API module (FastAPI)
│   ├── routes/              # HTTP endpoint route handlers
│   ├── services/            # Business & inference service layers
│   ├── schemas/             # Pydantic request/response schemas
│   └── database/            # SQLite connection and ORM models
│
├── frontend/                # React + Vite + Tailwind frontend application
│
├── src/                     # Core ML research & engineering source code
│   ├── data/                # Dataset loaders, auditing & preprocessing
│   ├── models/              # Neural network architectures & wrappers
│   ├── training/            # Training loops, loss functions & optimizers
│   ├── evaluation/          # Metrics, confusion matrices & benchmark validation
│   ├── explainability/      # Grad-CAM heatmap extraction routines
│   └── utils/               # Hardware detection, configuration loaders, logging
│
├── configs/                 # YAML configuration files (models, datasets, pipeline)
│
├── data/                    # Data storage (git-ignored raw/processed splits)
│   ├── raw/                 # Immutable raw benchmarks (PlantVillage, PlantDoc)
│   ├── interim/             # Intermediate transformed representations
│   ├── processed/           # Standardized, audited images
│   ├── splits/              # Train/validation/test manifest indices
│   └── metadata/            # Class mappings, audit logs and schemas
│
├── models/                  # Trained model checkpoints and serialized weights
│
├── experiments/             # Experiment run tracking and parameter dumps
│
├── reports/                 # Project documentation & visual evaluation artifacts
│   ├── dataset_audit/       # Data validation logs, corruption & duplicate checks
│   ├── metrics/             # Classification reports, ROC & PR curves
│   ├── figures/             # Confusion matrices and Grad-CAM visualizations
│   └── external_validation/ # PlantDoc cross-domain evaluation reports
│
├── scripts/                 # CLI entry points and orchestration utilities
├── tests/                   # Automated Pytest suite
├── README.md                # Project documentation
├── requirements.txt         # Project dependencies
└── .gitignore               # Ignored binaries, venv, and checkpoints
```

---

## 5. Development Roadmap (Six Phases)
- **Phase 1: Project Foundation** *(Current)*
  - Establish complete directory architecture.
  - Python 3.12 environment with multi-device hardware acceleration (MPS, CUDA, CPU).
  - YAML configuration specifications.
  - Image auditing, corruption scanning, and hash-based duplicate detection pipeline.
  - Test suite for environmental and data invariants.
- **Phase 2: Data Pipeline & Preprocessing**
  - Dataset ingestion and class indexing.
  - Stratified 70/15/15 train/val/test splitting.
  - Class imbalance handling and augmentation strategies.
- **Phase 3: Model Architecture, Training & Explainability**
  - ResNet18 transfer learning baseline.
  - PyTorch training pipeline with early stopping and checkpointing.
  - Grad-CAM explainability integration.
- **Phase 4: Backend API & Persistence**
  - FastAPI inference server.
  - Diagnostic history and recommendation engine with SQLite.
- **Phase 5: Frontend Interface**
  - React + Vite dashboard.
  - Interactive image upload, prediction breakdown, and heatmap overlays.
- **Phase 6: Integration, External Validation & System Hardening**
  - Cross-domain validation against real-world PlantDoc dataset.
  - Performance profiling, documentation, and final deployment packaging.

---

## 6. Environment Setup

### Prerequisites
- Python 3.12 installed.
- Terminal with access to bash/zsh.

### Setup Instructions
```bash
# 1. Create a virtual environment using Python 3.12
python3.12 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Upgrade pip and install Phase 1 dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 7. Dataset Placement Instructions

The system expects two primary datasets placed in `data/raw/`:

### A. PlantVillage (Primary Training Dataset)
Place the extracted PlantVillage color images into:
`data/raw/plantvillage/raw/color/`
And the leaf mapping file into:
`data/raw/plantvillage/leaf-map.json`

The 10 recognized tomato classes are:
- `Tomato___Bacterial_spot`
- `Tomato___Early_blight`
- `Tomato___Late_blight`
- `Tomato___Leaf_Mold`
- `Tomato___Septoria_leaf_spot`
- `Tomato___Spider_mites Two-spotted_spider_mite`
- `Tomato___Target_Spot`
- `Tomato___Tomato_Yellow_Leaf_Curl_Virus`
- `Tomato___Tomato_mosaic_virus`
- `Tomato___healthy`

### B. PlantDoc (External In-The-Wild Evaluation Dataset)
Place the extracted PlantDoc dataset into:
`data/raw/PlantDoc-Dataset/`

---

## 8. Dataset Audit & Group-Aware Splitting

### Step 1: Run Full Dataset Audit & Verification
Scans all images, checks header integrity, identifies exact duplicates via SHA-256, and generates reports:
```bash
python scripts/audit_datasets.py
```
Outputs are written to:
- `reports/dataset_audit/dataset_inventory.md`
- `reports/dataset_audit/class_distribution.csv`
- `reports/dataset_audit/corrupted_images.csv`
- `reports/dataset_audit/duplicate_report.csv`
- `data/metadata/plantvillage_metadata.json`
- `data/metadata/plantdoc_metadata.json`

### Step 2: Generate Group-Aware Splits (Zero-Leakage)
Splits PlantVillage into 70% Train, 15% Validation, and 15% Test while guaranteeing that leaf sequence groups and identical hashes never cross split boundaries:
```bash
python scripts/create_splits.py
```
Manifests are saved to:
- `data/splits/train.csv` (12,697 images)
- `data/splits/val.csv` (2,717 images)
- `data/splits/test.csv` (2,732 images)

---

## 9. Model Training (ResNet18 Transfer Learning)

Train the ResNet18 model using staged transfer learning (head warm-up followed by fine-tuning `layer4` and classification head):
```bash
python scripts/train_model.py --epochs-head 2 --epochs-finetune 3 --batch-size 64 --num-workers 4
```
Hardware acceleration automatically utilizes Apple Silicon MPS (`mps`), NVIDIA CUDA (`cuda`), or CPU fallback. Checkpoints and experiment metadata are saved to:
- `models/best_resnet18.pth`
- `models/latest_resnet18.pth`
- `models/class_mapping.json`
- `models/training_config.json`
- `experiments/training_history.json`

---

## 10. Model Evaluation

### A. Internal Test Set Evaluation (Untouched 15% Split)
Evaluate the selected model on the 2,732 held-out PlantVillage test images:
```bash
python scripts/evaluate_model.py
```
Outputs:
- Machine-readable metrics: `reports/metrics/internal_test_metrics.json`
- Confusion matrices: `reports/figures/internal_test_confusion_matrix.png` and `internal_test_confusion_matrix_normalized.png`

### B. External In-The-Wild Evaluation (PlantDoc Benchmark)
Evaluate generalization against real-world, in-the-wild photography from PlantDoc:
```bash
python scripts/evaluate_external.py
```
Outputs:
- Machine-readable metrics: `reports/external_validation/plantdoc_metrics.json`
- Confusion matrices: `reports/external_validation/plantdoc_external_confusion_matrix.png`
- Domain shift analysis report: `reports/external_validation/external_validation_report.md`

---

## 11. Explainable AI & Model Interpretability (Grad-CAM)

### A. What is Grad-CAM in AGRI-X?
Gradient-weighted Class Activation Mapping (Grad-CAM) produces coarse 2D heatmaps of visual attribution indicating the salient discriminative regions the convolutional neural network attends to when diagnosing a leaf pathology. It allows agriculturalists and researchers to verify whether the AI model focuses on actual pathogenic lesions (such as necrotic spots or fungal mycelia) rather than background cards, petioles, or image artifacts.

### B. Generate Explanation for a Single Leaf Image
Generate a 4-panel diagnostic visual (Original Image, Grayscale Activation Map, Color Attribution Overlay, and Top Alternative Class Probabilities):
```bash
python -c "
import torch
from pathlib import Path
from src.models.resnet18 import build_model
from src.explainability.explanation_service import ExplanationService

ckpt = torch.load('models/best_resnet18.pth', map_location='cpu')
class_mapping = {int(k): v for k, v in ckpt['class_mapping'].items()}
model = build_model(num_classes=ckpt['num_classes'], pretrained=False)
model.load_state_dict(ckpt['model_state_dict'])

service = ExplanationService(model=model, class_mapping=class_mapping, device=torch.device('cpu'))
result = service.explain_image('data/raw/plantvillage/raw/color/Tomato___Bacterial_spot/3e4ca861-5f1d-43c1-9b31-225455da4533___GCREC_Bact.Sp 3098.JPG')
service.save_explanation_panel(result, 'reports/figures/gradcam/single_explanation_panel.png')
print('Diagnostic panel saved to reports/figures/gradcam/single_explanation_panel.png')
"
```

### C. Batch Explainability Generation
Generate visual explanation panels and record explanation metadata across held-out splits:
```bash
python scripts/generate_gradcam.py --limit-per-class 2
```
Outputs:
- Diagnostic panels: `reports/figures/gradcam/`
- Metadata: `reports/explainability/gradcam_metadata.csv`

### D. Misclassification & Error Attribution Analysis
Inspect high-confidence and low-confidence classification errors, comparing predicted class attributions against true ground-truth class counterfactuals:
```bash
python scripts/analyze_misclassifications.py
```
Outputs:
- Error & counterfactual panels: `reports/figures/misclassifications/`
- Error metadata: `reports/explainability/misclassified_examples.csv`

### E. Controlled Robustness & Perturbation Experiments
Evaluate model prediction stability and confidence drift across non-destructive visual transformations (brightness, contrast, affine rotation, blur, downscaling):
```bash
python scripts/run_robustness_experiments.py
```
Outputs:
- Robustness panels: `reports/figures/robustness/`
- Detailed metrics CSV: `reports/explainability/robustness_results.csv`
- Executive summary JSON: `reports/explainability/robustness_summary.json`
- Comprehensive evaluation report: `reports/explainability/explainability_evaluation_report.md`

### F. Grad-CAM Methodological Limitations
1. **Attribution, not biological proof:** Grad-CAM reflects model feature correlations, not definitive biological causation.
2. **Coarse resolution:** Attributions are calculated from $7 \times 7$ feature maps in `layer4`, yielding smooth regional heatmaps rather than fine cellular boundaries.
3. **Closed-world calibration:** Softmax probabilities reflect relative confidence among the 10 known classes, not absolute real-world probabilities.

---

## 13. Local AI Web Application (FastAPI + React Integration)

AGRI-X operates as a local AI web application running entirely on your machine.
- **Backend Service**: FastAPI server communicating with the trained ResNet18 PyTorch model and Grad-CAM interpreter on `http://127.0.0.1:8000`.
- **Frontend Dashboard**: React + Vite application running on `http://localhost:5173`.
- **Privacy & Security**: Zero cloud dependencies; leaf photographs never leave your local environment.

### A. Local API Endpoints
| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status, model readiness, compute device (`mps`), and class count |
| `POST` | `/api/v1/predict` | Multipart image upload for ResNet18 inference returning predicted pathology and top-5 Softmax probability scores |
| `POST` | `/api/v1/explain` | Computes real Grad-CAM attribution heatmaps from `layer4[-1]` and returns base64-encoded PNG overlays |

### B. Launching the Complete Local System

Open two terminal windows:

#### Terminal 1: Launch the Local Python AI Service
```bash
# 1. Activate Python virtual environment
source .venv/bin/activate

# 2. Launch FastAPI with Uvicorn
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
Swagger interactive API documentation will be available at: `http://127.0.0.1:8000/docs`.

#### Terminal 2: Launch the React Frontend
```bash
# 1. Enter the frontend directory
cd frontend

# 2. Launch the Vite development server
npm run dev
```
Open your browser at: **`http://localhost:5173`**.

---

## 14. Running Automated Tests
Run the entire comprehensive test suite (27 tests across Phase 1, 2, 3, and 5):
```bash
pytest tests/ -v
```
