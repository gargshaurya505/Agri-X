# AGRI-X: Explainable Crop Disease Detection

A machine learning system for tomato crop disease diagnosis with visual explanations powered by Grad-CAM. Built as a college major project using PyTorch, FastAPI, and React. Everything runs locally on your computer—no cloud services, no remote data uploads.

---

## What is AGRI-X?

Standard image classification models act like black boxes: you feed in a leaf photo, and the model outputs a label like "Early Blight 92%" without showing *why* it made that choice. In agriculture, trusting a bad prediction could ruin an entire crop bed through unnecessary or wrong pesticide treatment.

AGRI-X addresses this by coupling a fine-tuned ResNet-18 model with **Grad-CAM (Gradient-weighted Class Activation Mapping)**. Whenever it predicts a pathology, it generates a heat map highlighting the exact regions on the leaf (lesions, fungal spots, chlorosis) that influenced its decision.

### Key Highlights
- **10 Tomato Conditions**: Classifies 9 common foliar diseases plus healthy leaves.
- **Visual Attribution**: Generates heatmaps from the final convolutional layer (`layer4`) to verify the network is looking at lesions, not background noise.
- **In-The-Wild Evaluation**: Tested against both controlled benchmark datasets (PlantVillage) and noisy, in-field photos (PlantDoc) to measure domain shift.
- **Local-First Architecture**: Runs on Apple Silicon (MPS) or CUDA/CPU with a FastAPI backend and a clean React + Tailwind CSS dashboard.

---

## Supported Disease Classes

The model currently recognizes 10 tomato leaf classes:

| Class Name | Pathogen / Condition |
|---|---|
| Bacterial Spot | *Xanthomonas campestris pv. vesicatoria* |
| Early Blight | *Alternaria solani* |
| Late Blight | *Phytophthora infestans* |
| Leaf Mold | *Passalora fulva* |
| Septoria Leaf Spot | *Septoria lycopersici* |
| Two-Spotted Spider Mite | *Tetranychus urticae* |
| Target Spot | *Corynespora cassiicola* |
| Tomato Yellow Leaf Curl Virus (TYLCV) | Begomovirus |
| Tomato Mosaic Virus (ToMV) | Tobamovirus |
| Healthy | Uninfected foliage (*Solanum lycopersicum*) |

---

## How It Works

```
[ Leaf Photograph ]
         │
         ▼
[ FastAPI Service ] ──> Preprocessing (224x224, ImageNet normalization)
         │
         ▼
[ PyTorch ResNet-18 ] ──> Softmax Probabilities (Top-5 Predictions)
         │
         ▼
[ Grad-CAM Hook ] ──> Extracts gradients from layer4[-1]
         │
         ▼
[ React + Vite UI ] <── Returns JSON result + Base64 Heatmap overlay
```

1. **Frontend**: The user drops an image into the React interface.
2. **Inference**: The image is posted to a local FastAPI endpoint (`/api/v1/predict`), normalized, and fed into the PyTorch ResNet-18 backbone.
3. **Attribution**: If requested (`/api/v1/explain`), Grad-CAM computes gradients with respect to the target class activations at the final convolutional layer, applies a ReLU filter, and overlays the heat map onto the original image.
4. **Display**: The UI displays confidence percentages, top-5 candidate distributions, agronomic advice, and the visual attribution panel.

---

## Tech Stack

- **Machine Learning**: Python 3.12, PyTorch, Torchvision, Scikit-learn, PIL, NumPy, Pandas
- **Interpretability**: Custom Grad-CAM implementation (`src/explainability/grad_cam.py`)
- **Backend API**: FastAPI, Uvicorn, Pydantic
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React, Recharts
- **Storage**: Browser `localStorage` for analysis history and user settings

---

## Project Structure

```
Agrii/
├── api/                     # FastAPI backend
│   ├── routes/              # Health, prediction, and explainability endpoints
│   ├── schemas/             # Pydantic models for validation
│   └── services/            # Lifespan model loader and Grad-CAM handler
├── configs/                 # YAML configs for dataset, training, and augmentations
├── data/                    # Datasets (git-ignored) and train/val/test split manifests
│   ├── raw/                 # PlantVillage & PlantDoc datasets
│   └── splits/              # Zero-leakage split CSVs (train, val, test)
├── frontend/                # React + Vite application
│   └── src/
│       ├── components/      # UI components (Upload, Results, Charts, Navbar)
│       ├── pages/           # Landing, Dashboard, Detect, Library, History
│       └── services/        # Axios API clients & local history store
├── models/                  # Checkpoints, class mappings, and training metadata
├── reports/                 # Audit files, confusion matrices, and Grad-CAM panels
├── scripts/                 # CLI tools for auditing, training, and evaluation
├── src/                     # Core ML logic (DataLoader, ResNet, Grad-CAM)
└── tests/                   # Pytest test suite (27 tests)
```

---

## Quick Start (Running Locally)

### 1. Prerequisites
- Python 3.12
- Node.js 18+ and npm
- A modern browser (Chrome, Safari, Firefox, Edge)

### 2. Setup the Python Environment
```bash
# Clone the repository
git clone https://github.com/gargshaurya505/Agri-X.git
cd Agri-X

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Setup the Frontend
```bash
cd frontend
npm install
cd ..
```

### 4. Running the Application

Open two terminal tabs:

**Tab 1 (FastAPI Backend):**
```bash
source .venv/bin/activate
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
*Health check & Swagger docs will be live at `http://127.0.0.1:8000/docs`.*

**Tab 2 (React Frontend):**
```bash
cd frontend
npm run dev
```
*Open **`http://localhost:5173`** in your browser.*

---

## Training & Evaluation Notes

### Dataset Splitting & Leakage Prevention
During initial testing, we found duplicate photos in the raw PlantVillage dataset. If identical leaves fall into both the training and test splits, the test metrics become artificially inflated.
To solve this:
- Exact image duplicates were identified and removed using SHA-256 hashes.
- Images were split 70% Train (12,697 images), 15% Validation (2,717 images), and 15% Test (2,732 images) using grouped splitting (`scripts/create_splits.py`) so related leaf sequences never cross splits.

### Training Procedure
We used a staged transfer learning approach:
1. **Warmup Phase**: The pretrained ResNet-18 convolutional backbone is frozen; only the newly attached classification head is trained for 2 epochs.
2. **Fine-Tuning Phase**: The final residual block (`layer4`) along with the linear classifier are unfrozen and trained with AdamW and cosine annealing learning rate scheduling.

```bash
python scripts/train_model.py --epochs-head 2 --epochs-finetune 3 --batch-size 64
```

### Results Summary
- **Internal Test Set (PlantVillage)**:
  - Accuracy: **98.43%**
  - Macro F1: **98.01%**
  - Most confused classes: *Early Blight* vs *Target Spot* due to similar concentric ring lesion patterns.
- **External Real-World Test Set (PlantDoc)**:
  - Accuracy: **33.48%**
  - Evaluated on in-the-wild photos with complex backgrounds (dirt, hands, sky, overlapping foliage). This drop highlights real-world domain shift—a central discussion point in our major project defense.

---

## Explainability (Grad-CAM)

To see the visual explanations from the command line:

```bash
# Generate explanation panels across sample test images
python scripts/generate_gradcam.py --limit-per-class 2

# Run robustness experiments (brightness, rotation, blur perturbations)
python scripts/run_robustness_experiments.py
```

Generated panels are stored in `reports/figures/gradcam/`.

---

## Running Tests

To verify that the model architecture, image validation pipeline, API routes, and Grad-CAM hooks are working properly:

```bash
pytest tests/ -v
```

All 27 integration and unit tests should pass.

---

## Author & Academic Context

- **Author**: Shaurya Garg
- **Degree**: Bachelor of Technology (Computer Science & Engineering)
- **Project**: Major Project / Capstone Defense
- **Institution**: Graphic Era University
