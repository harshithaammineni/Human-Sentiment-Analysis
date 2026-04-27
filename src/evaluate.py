"""Evaluation helpers: collect predictions/probabilities for any model
and emit JSON metrics + PNG confusion matrices.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from . import config as C
from .utils import compute_metrics, get_device, plot_confusion_matrix, save_metrics


# -------------------------------------------------------------------------
# Generic predictor
# -------------------------------------------------------------------------
@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    loader: DataLoader,
    forward_fn: Callable,
    device: Optional[torch.device] = None,
    return_ids: bool = True,
) -> Dict[str, np.ndarray]:
    """Run ``model`` over ``loader`` and return labels, preds, probs (and ids).

    Expects ``forward_fn(model, batch, device)`` to return ``(logits, labels)``.
    Supports the four batch layouts we use:
        (images, labels, ids)
        (feat_vec, labels)               -- fusion
        (images, texts, labels, ids)     -- CLIP
    """
    device = device or get_device()
    model = model.to(device).eval()

    all_labels: List[int] = []
    all_preds: List[int] = []
    all_probs: List[np.ndarray] = []
    all_ids: List[str] = []

    for batch in tqdm(loader, leave=False, desc="predict"):
        logits, labels = forward_fn(model, batch, device)
        probs = F.softmax(logits, dim=1)
        preds = probs.argmax(dim=1)

        all_labels.extend(labels.detach().cpu().tolist())
        all_preds.extend(preds.detach().cpu().tolist())
        all_probs.append(probs.detach().cpu().numpy())

        if return_ids:
            ids = _extract_ids(batch)
            if ids is not None:
                all_ids.extend(ids)

    out = {
        "y_true": np.asarray(all_labels),
        "y_pred": np.asarray(all_preds),
        "probs":  np.concatenate(all_probs, axis=0) if all_probs else np.empty((0, C.NUM_CLASSES)),
    }
    if return_ids and all_ids:
        out["ids"] = np.asarray(all_ids)
    return out


def _extract_ids(batch):
    """Pull sample_ids from any of the supported batch layouts."""
    if isinstance(batch, (list, tuple)):
        if len(batch) == 3:
            return list(batch[2])
        if len(batch) == 4:
            return list(batch[3])
    return None


# -------------------------------------------------------------------------
# One-stop evaluator: predict + metrics + plot CM
# -------------------------------------------------------------------------
def evaluate_and_save(
    model: nn.Module,
    loader: DataLoader,
    forward_fn: Callable,
    name: str,
    save_dir_metrics: Path = C.METRICS_DIR,
    save_dir_cm: Path = C.CM_DIR,
    save_dir_preds: Path = C.PREDICTIONS_DIR,
    class_names: Sequence[str] = C.CLASS_NAMES,
    device: Optional[torch.device] = None,
) -> Dict:
    """Predict, compute metrics, save JSON + CSV + confusion-matrix PNG.

    Returns the metrics dict (also written to disk).
    """
    out = collect_predictions(model, loader, forward_fn, device=device, return_ids=True)
    y_true = out["y_true"]; y_pred = out["y_pred"]; probs = out["probs"]
    metrics = compute_metrics(y_true, y_pred, class_names=class_names)
    metrics["model_name"] = name
    metrics["n_test"] = int(len(y_true))

    # Save metrics
    save_metrics(metrics, Path(save_dir_metrics) / f"{name}_metrics.json")

    # Save predictions for downstream fusion / analysis
    pred_df = pd.DataFrame({
        "sample_id": out.get("ids", np.arange(len(y_true))),
        "y_true": y_true,
        "y_pred": y_pred,
        **{f"prob_{class_names[i]}": probs[:, i] for i in range(probs.shape[1])},
    })
    pred_path = Path(save_dir_preds) / f"{name}_predictions.csv"
    pred_path.parent.mkdir(parents=True, exist_ok=True)
    pred_df.to_csv(pred_path, index=False)

    # Plot CM
    plot_confusion_matrix(
        y_true, y_pred,
        class_names=list(class_names),
        title=f"{name} (acc={metrics['accuracy']:.3f}, f1m={metrics['macro_f1']:.3f})",
        save_path=Path(save_dir_cm) / f"{name}_cm.png",
        normalize=True,
    )
    return metrics


# -------------------------------------------------------------------------
# Comparison table
# -------------------------------------------------------------------------
def comparison_row(metrics: Dict, model_label: str, input_label: str) -> Dict:
    return {
        "model": model_label,
        "input": input_label,
        "accuracy": round(metrics["accuracy"], 4),
        "macro_f1": round(metrics["macro_f1"], 4),
        "weighted_f1": round(metrics["weighted_f1"], 4),
    }


def majority_baseline(y_true: Sequence[int], num_classes: int = C.NUM_CLASSES) -> Dict:
    y_true = np.asarray(y_true)
    counts = np.bincount(y_true, minlength=num_classes)
    majority = int(counts.argmax())
    y_pred = np.full_like(y_true, fill_value=majority)
    return compute_metrics(y_true, y_pred)
