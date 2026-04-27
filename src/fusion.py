"""Build the fusion feature vectors and PyTorch Dataset for the fusion MLP.

The fusion model consumes ``[face_probs(3) + image_probs(3) + num_faces_norm + face_flag]``
per sample and predicts the final 3-class label. Per-image face
probabilities are computed by averaging per-face probabilities (label
fusion). Images with no detected face get a neutral fallback prior.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from . import config as C


NUM_FACES_CAP: int = 5  # used to normalise the count to [0, 1]


# -------------------------------------------------------------------------
# Build per-image face probabilities from per-face predictions
# -------------------------------------------------------------------------
def aggregate_face_predictions(
    face_pred_csv: Union[str, Path],
    master_df: pd.DataFrame,
    no_face_prior: Optional[Sequence[float]] = None,
    class_names: Sequence[str] = C.CLASS_NAMES,
) -> pd.DataFrame:
    """Average face-model probabilities across all faces in the same image.

    Parameters
    ----------
    face_pred_csv : path
        CSV produced by ``evaluate.evaluate_and_save`` for the face model
        (one row per face crop, with prob_negative / prob_neutral / prob_positive).
    master_df : DataFrame
        Master CSV (one row per image). Must contain ``sample_id``,
        ``num_faces``, ``label_id``, ``split``.
    no_face_prior : list of 3 floats, optional
        Probability vector to use for images with zero faces. Defaults to
        the global label distribution of the *training* split.
    """
    face_pred_df = pd.read_csv(face_pred_csv)
    prob_cols = [f"prob_{c}" for c in class_names]

    # Average probabilities per sample_id, renaming straight to the final
    # face_prob_<class> columns the fusion model expects.
    agg = (
        face_pred_df.groupby("sample_id")[prob_cols]
        .mean()
        .reset_index()
        .rename(columns={f"prob_{c}": f"face_prob_{c}" for c in class_names})
    )

    merged = master_df.merge(agg, on="sample_id", how="left")

    # Determine prior for no-face images
    if no_face_prior is None:
        train = master_df[master_df["split"] == "train"]
        counts = train["label_id"].value_counts().sort_index()
        prior = counts.values / counts.sum()
    else:
        prior = np.asarray(no_face_prior, dtype=float)

    for i, c in enumerate(class_names):
        col = f"face_prob_{c}"
        merged.loc[merged[col].isna(), col] = float(prior[i])

    merged["face_detected_flag"] = (merged["num_faces"] > 0).astype(int)
    merged["num_faces_norm"] = (
        merged["num_faces"].clip(lower=0, upper=NUM_FACES_CAP) / NUM_FACES_CAP
    )
    return merged


def attach_image_predictions(
    merged_df: pd.DataFrame,
    image_pred_csv: Union[str, Path],
    class_names: Sequence[str] = C.CLASS_NAMES,
) -> pd.DataFrame:
    """Add full-image model probabilities (one row per image) to the merged df."""
    img_df = pd.read_csv(image_pred_csv)
    keep = ["sample_id"] + [f"prob_{c}" for c in class_names]
    img_df = img_df[keep].copy()
    rename = {f"prob_{c}": f"image_prob_{c}" for c in class_names}
    img_df = img_df.rename(columns=rename)
    return merged_df.merge(img_df, on="sample_id", how="left")


# -------------------------------------------------------------------------
# Convert merged frame to a tensor dataset
# -------------------------------------------------------------------------
FUSION_FEATURE_COLS = [
    "face_prob_negative", "face_prob_neutral", "face_prob_positive",
    "image_prob_negative", "image_prob_neutral", "image_prob_positive",
    "num_faces_norm", "face_detected_flag",
]


class FusionFeatureDataset(Dataset):
    """In-memory dataset producing (feature_vec, label) pairs."""

    def __init__(
        self, df: pd.DataFrame,
        feature_cols: Sequence[str] = FUSION_FEATURE_COLS,
        label_col: str = "label_id",
    ) -> None:
        # Drop rows with missing image probs (e.g. predictions not yet generated)
        df = df.dropna(subset=list(feature_cols)).reset_index(drop=True)
        self.X = df[list(feature_cols)].astype(np.float32).values
        self.y = df[label_col].astype(np.int64).values
        self.sample_ids = df["sample_id"].values

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return torch.from_numpy(self.X[idx]), torch.tensor(self.y[idx], dtype=torch.long)


def build_fusion_splits(
    merged_df: pd.DataFrame,
    feature_cols: Sequence[str] = FUSION_FEATURE_COLS,
) -> Dict[str, FusionFeatureDataset]:
    out = {}
    for split in ("train", "val", "test"):
        sub = merged_df[merged_df["split"] == split]
        out[split] = FusionFeatureDataset(sub, feature_cols=feature_cols)
    return out


# -------------------------------------------------------------------------
# Forward-fn for evaluator (so we can reuse evaluate.collect_predictions)
# -------------------------------------------------------------------------
def fusion_forward_with_ids(model, batch, device):
    """Adapter that returns logits + labels for evaluator's collect_predictions.

    Our FusionFeatureDataset yields (X, y) only -- the evaluator expects to
    optionally find ids in batch[2:]; we therefore wrap it via a custom
    collate that injects sample_ids if needed (see notebook 06).
    """
    feats, labels = batch[0], batch[1]
    feats = feats.to(device, non_blocking=True)
    labels = labels.to(device, non_blocking=True)
    logits = model(feats)
    return logits, labels
