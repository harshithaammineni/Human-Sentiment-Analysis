"""General utilities: seeding, device selection, metric/plot helpers."""
from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from . import config as C


# -------------------------------------------------------------------------
# Reproducibility / device
# -------------------------------------------------------------------------
def seed_everything(seed: int = 42) -> None:
    """Set every RNG we touch."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    # CuDNN: trade a tiny bit of speed for determinism
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device(preferred: str = "cpu") -> torch.device:
    """Return the local CPU device used by the notebooks."""
    return torch.device("cpu")


# -------------------------------------------------------------------------
# Metrics
# -------------------------------------------------------------------------
def compute_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    class_names: Sequence[str] = C.CLASS_NAMES,
) -> Dict[str, Union[float, Dict]]:
    """Accuracy + macro/weighted F1 + per-class P/R/F + classification report."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=list(range(len(class_names))),
        zero_division=0,
    )
    per_class = {
        name: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i])}
        for i, name in enumerate(class_names)
    }
    report = classification_report(
        y_true, y_pred, target_names=list(class_names),
        zero_division=0, output_dict=True,
    )
    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "classification_report": report,
    }


def save_metrics(metrics: Dict, path: Union[str, Path]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)


# -------------------------------------------------------------------------
# Plots
# -------------------------------------------------------------------------
def plot_confusion_matrix(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    class_names: Sequence[str] = C.CLASS_NAMES,
    title: str = "Confusion Matrix",
    save_path: Union[str, Path, None] = None,
    normalize: bool = True,
) -> np.ndarray:
    cm = confusion_matrix(
        y_true, y_pred, labels=list(range(len(class_names))),
    )
    cm_display = cm.astype(float)
    if normalize:
        row_sums = cm_display.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        cm_display = cm_display / row_sums

    fig, ax = plt.subplots(figsize=(5.0, 4.2))
    sns.heatmap(
        cm_display, annot=True, fmt=".2f" if normalize else "d",
        cmap="Blues", xticklabels=class_names, yticklabels=class_names,
        cbar=True, square=True, ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return cm


def plot_training_curves(
    history: Dict[str, List[float]],
    title: str = "Training curves",
    save_path: Union[str, Path, None] = None,
) -> None:
    """Plot loss + accuracy curves from a history dict produced by train.py."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].plot(history.get("train_loss", []), label="train")
    axes[0].plot(history.get("val_loss", []), label="val")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
    axes[0].set_title("Loss"); axes[0].legend(); axes[0].grid(alpha=0.3)

    axes[1].plot(history.get("train_acc", []), label="train")
    axes[1].plot(history.get("val_acc", []), label="val")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy")
    axes[1].set_title("Accuracy"); axes[1].legend(); axes[1].grid(alpha=0.3)

    fig.suptitle(title)
    fig.tight_layout()
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# -------------------------------------------------------------------------
# Misc
# -------------------------------------------------------------------------
def count_parameters(model: torch.nn.Module, trainable_only: bool = True) -> int:
    if trainable_only:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    return sum(p.numel() for p in model.parameters())


def format_param_count(n: int) -> str:
    for unit in ("", "K", "M", "B"):
        if abs(n) < 1000:
            return f"{n:.1f}{unit}"
        n /= 1000.0
    return f"{n:.1f}T"


def chunked(seq: Iterable, size: int) -> Iterable[List]:
    """Yield successive ``size``-sized lists from ``seq``."""
    bucket: List = []
    for x in seq:
        bucket.append(x)
        if len(bucket) == size:
            yield bucket
            bucket = []
    if bucket:
        yield bucket
