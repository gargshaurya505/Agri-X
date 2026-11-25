# Raw Dataset Instructions

This directory holds the raw input datasets for the **AGRI-X** project.
Raw datasets are treated as immutable read-only records.

## Required Datasets

### 1. PlantVillage (Primary Training Dataset)
Place the extracted PlantVillage dataset under:
`data/raw/plantvillage/`

Expected folder layout for the 10 tomato classes:
```text
data/raw/plantvillage/
├── Tomato___Bacterial_spot/
├── Tomato___Early_blight/
├── Tomato___Late_blight/
├── Tomato___Leaf_Mold/
├── Tomato___Septoria_leaf_spot/
├── Tomato___Spider_mites Two-spotted_spider_mite/
├── Tomato___Target_Spot/
├── Tomato___Tomato_Yellow_Leaf_Curl_Virus/
├── Tomato___Tomato_mosaic_virus/
└── Tomato___healthy/
```

### 2. PlantDoc (External Evaluation Dataset)
Place the extracted PlantDoc dataset under:
`data/raw/plantdoc/`

Expected folder layout:
```text
data/raw/plantdoc/
├── train/
└── test/
```

## Note on Dataset Provisioning
Neither dataset is bundled in this repository to prevent repository bloat and comply with dataset distribution licenses.
Once you place the datasets in `data/raw/`, run the dataset audit pipeline:
```bash
python scripts/audit_datasets.py
```
