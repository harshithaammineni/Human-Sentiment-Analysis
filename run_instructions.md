# Run Instructions (Local CPU)

This project is configured to run on the local Windows machine using a CPU
Python kernel in VS Code/Jupyter.

## 1. Open The Correct Folder

Open this folder in VS Code:

```text
C:\Users\hp\Desktop\CNN\EEEM068-Human-Sentiment-Analysis
```

Use the notebook kernel picker to select this local CPU kernel:

```text
CNN Local CPU (Python 3.13)
```

It points to this local Python interpreter:

```text
C:\Users\hp\AppData\Local\Programs\Python\Python313\python.exe
```

The first notebook cell should print:

```text
Project root: C:\Users\hp\Desktop\CNN\EEEM068-Human-Sentiment-Analysis
```

## 2. Install Dependencies

Run from the project root:

```bash
cd C:\Users\hp\Desktop\CNN\EEEM068-Human-Sentiment-Analysis
pip install -r requirements.txt
```

The notebooks are CPU-first:

- `src/config.py::TrainConfig.device` is `cpu`
- notebook `device` variables are `torch.device("cpu")`
- notebook DataLoaders use `num_workers=0` and `pin_memory=False`

## 3. Verify Data

The expected local layout is:

```text
data/raw/
+-- english_{train,dev,test}.txt
+-- image_index_{train,dev,test}.txt
+-- sentiment_{train,dev,test}.txt
+-- images/
    +-- train/  # 20,240 jpg files
    +-- dev/    # 5,063 jpg files
    +-- test/   # 5,067 jpg files
```

Verify it:

```bash
python scripts/download_data.py --verify-only --strict-verify
```

## 4. Notebook Order

| # | Notebook | What it produces |
|---|---|---|
| 01 | `01_dataset_preparation.ipynb` | `data/processed/msctd_master.csv`, EDA plots |
| 02 | `02_face_extraction.ipynb` | `data/faces/`, `data/processed/face_metadata.csv` |
| 03 | `03_face_model_training.ipynb` | `outputs/model_checkpoints/face_resnet18.pth`, metrics, confusion matrix |
| 04 | `04_augmentation_robustness.ipynb` | `data/degraded_faces/`, robustness CSV |
| 05 | `05_full_image_model.ipynb` | `outputs/model_checkpoints/full_image_resnet50_mlp.pth`, metrics |
| 06 | `06_fusion_model.ipynb` | `outputs/model_checkpoints/fusion_mlp.pth`, final comparison table |
| 07 | `07_multimodal_extra_credit.ipynb` | `outputs/model_checkpoints/clip_multimodal_classifier.pth`, metrics |

## 5. CPU Runtime Notes

CPU execution is correct but slow for notebooks 02-07, especially MTCNN face
extraction, ResNet training, and CLIP. Keep the machine awake while long cells
run.

If imports fail, restart the kernel after opening the project folder above.
