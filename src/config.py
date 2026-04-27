"""Central configuration for the EEEM068 Human Sentiment Analysis project.

All paths, hyperparameters and label mappings live here so that notebooks
remain thin orchestration layers and every experiment is reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
FACES_DIR: Path = DATA_DIR / "faces"
DEGRADED_DIR: Path = DATA_DIR / "degraded_faces"

OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
METRICS_DIR: Path = OUTPUTS_DIR / "metrics"
CM_DIR: Path = OUTPUTS_DIR / "confusion_matrices"
PLOTS_DIR: Path = OUTPUTS_DIR / "plots"
PREDICTIONS_DIR: Path = OUTPUTS_DIR / "predictions"
CKPT_DIR: Path = OUTPUTS_DIR / "model_checkpoints"
TABLES_DIR: Path = OUTPUTS_DIR / "tables"

REPORT_FIG_DIR: Path = PROJECT_ROOT / "report" / "figures"
REPORT_TAB_DIR: Path = PROJECT_ROOT / "report" / "tables"

# Master CSVs
MASTER_CSV: Path = PROCESSED_DIR / "msctd_master.csv"
FACE_METADATA_CSV: Path = PROCESSED_DIR / "face_metadata.csv"
DEGRADED_FACE_METADATA_CSV: Path = PROCESSED_DIR / "degraded_face_metadata.csv"
SPLIT_SUMMARY_CSV: Path = TABLES_DIR / "dataset_split_summary.csv"


# -------------------------------------------------------------------------
# Labels
# -------------------------------------------------------------------------
LABEL_MAP: Dict[str, int] = {"negative": 0, "neutral": 1, "positive": 2}
INV_LABEL_MAP: Dict[int, str] = {v: k for k, v in LABEL_MAP.items()}
NUM_CLASSES: int = 3
CLASS_NAMES: List[str] = ["negative", "neutral", "positive"]


# -------------------------------------------------------------------------
# Splits
# -------------------------------------------------------------------------
@dataclass(frozen=True)
class SplitConfig:
    train: float = 0.70
    val: float = 0.15
    test: float = 0.15
    seed: int = 42


SPLIT = SplitConfig()


# -------------------------------------------------------------------------
# Image / face sizes
# -------------------------------------------------------------------------
FACE_SIZE: Tuple[int, int] = (224, 224)   # ResNet18 input
IMAGE_SIZE: Tuple[int, int] = (224, 224)  # ResNet50 / ViT input
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)


# -------------------------------------------------------------------------
# Training hyperparameters
# -------------------------------------------------------------------------
@dataclass
class TrainConfig:
    batch_size: int = 32
    num_workers: int = 0
    lr: float = 1e-4
    weight_decay: float = 1e-4
    epochs: int = 15
    early_stop_patience: int = 3
    grad_clip: float = 1.0
    label_smoothing: float = 0.0
    seed: int = 42
    device: str = "cpu"


# Per-stage configs (override defaults selectively)
FACE_TRAIN = TrainConfig(epochs=15, lr=1e-4)
FULL_IMAGE_TRAIN = TrainConfig(epochs=12, lr=3e-4)  # frozen backbone => higher lr ok
FUSION_TRAIN = TrainConfig(epochs=30, lr=1e-3, batch_size=64)
CLIP_TRAIN = TrainConfig(epochs=8, lr=1e-4, batch_size=32)


# -------------------------------------------------------------------------
# Model checkpoints
# -------------------------------------------------------------------------
FACE_CKPT: Path = CKPT_DIR / "face_resnet18.pth"
FACE_AUG_CKPT: Path = CKPT_DIR / "face_resnet18_augmented.pth"
FULL_IMAGE_CKPT: Path = CKPT_DIR / "full_image_resnet50_mlp.pth"
FUSION_CKPT: Path = CKPT_DIR / "fusion_mlp.pth"
CLIP_CKPT: Path = CKPT_DIR / "clip_multimodal_classifier.pth"


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
ALL_DIRS: List[Path] = [
    DATA_DIR, RAW_DIR, PROCESSED_DIR, FACES_DIR, DEGRADED_DIR,
    OUTPUTS_DIR, METRICS_DIR, CM_DIR, PLOTS_DIR, PREDICTIONS_DIR,
    CKPT_DIR, TABLES_DIR, REPORT_FIG_DIR, REPORT_TAB_DIR,
]


def ensure_dirs() -> None:
    """Create every project directory if missing. Safe to call repeatedly."""
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
