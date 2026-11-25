# PlantDoc External Evaluation & Domain Shift Analysis

## Executive Summary
This report analyzes the generalization of the AGRI-X ResNet18 model (trained on lab-conditioned PlantVillage benchmark) when deployed on real-world in-the-wild photography from PlantDoc.

## Quantitative Results (Confirmed Samples: 681)
- **Accuracy:** 33.48%
- **Macro Precision:** 21.46%
- **Macro Recall:** 23.92%
- **Macro F1 Score:** 20.16%
- **Weighted F1 Score:** 27.98%

## Excluded Categories & Sample Limitations
- **`Tomato leaf` (63 images):** Excluded because generic naming does not reliably verify health.
- **`Tomato two spotted spider mites leaf` (2 images):** Insufficient sample size for statistically meaningful performance evaluation.
- **`Tomato Target Spot`:** Not present in the PlantDoc collection.

## Domain Shift & Generalization Discussion
1. **Background Variance:** PlantVillage images feature homogeneous lab backgrounds (neutral grey/black cards), whereas PlantDoc photos contain complex field soils, dynamic sunlight glare, and mixed foliage.
2. **Multi-Scale Symptoms:** Real field conditions present multiple leaves per shot at varying focal depths, contrasting with PlantVillage's single-leaf centered framing.
3. **Co-infections & Occlusions:** Field leaves frequently display mechanical damage and secondary saprophytic fungi that do not appear in controlled lab culture datasets.
