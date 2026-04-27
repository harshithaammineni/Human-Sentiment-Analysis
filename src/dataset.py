"""MSCTD (En-De) dataset loading, parsing and PyTorch Dataset classes.

The MSCTD repo (https://github.com/XL2248/MSCTD) ships three parallel
files per split, all using a *line-indexed* format
``<line_num>\\t<content>``:

    english_<split>.txt      one English utterance per line
    sentiment_<split>.txt    integer label in {0,1,2} per line, aligned
                             1:1 with english_<split>.txt
    image_index_<split>.txt  one *scene* per line of the form
                             ``<scene_id>\\t[utt_idx, utt_idx, ...]``;
                             this groups utterances that belong to the
                             same dialogue scene.

Each **utterance has its own image** at
``data/raw/images/<split>/<utt_idx>.jpg`` (utt_idx is 0-indexed and
matches the 0-indexed line number in english/sentiment files). The
``image_index_*.txt`` scene groupings are dialogue context, not a way
to share images.

So we build a utterance-level DataFrame with one row per (image, text,
sentiment) triple. The ``scene_id`` column is preserved as a context
key and is used only for **scene-level stratified splitting** (so
utterances of the same dialogue land in the same split, avoiding
context leakage).

Master CSV columns:
    sample_id, image_path, scene_id, utterance_idx,
    text, label_text, label_id, split,
    num_faces (filled later by face_detection.py),
    face_paths (filled later by face_detection.py)
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
from PIL import Image
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from . import config as C


# -------------------------------------------------------------------------
# Raw MSCTD parsing
# -------------------------------------------------------------------------
# Native MSCTD label convention: 0 negative, 1 neutral, 2 positive --
# already aligned with our LABEL_MAP, but we re-validate to be safe.
_MSCTD_LABEL_TO_TEXT = {0: "negative", 1: "neutral", 2: "positive"}


def _strip_indexed_line(line: str) -> str:
    """MSCTD lines look like ``<line_num>\\t<content>``. Return the content."""
    line = line.rstrip("\n")
    parts = line.split("\t", 1)
    return parts[1] if len(parts) == 2 else parts[0]


def _read_indexed_lines(path: Path) -> List[str]:
    """Read a MSCTD ``<num>\\t<content>`` file -> list of contents."""
    with open(path, "r", encoding="utf-8") as fh:
        return [_strip_indexed_line(ln) for ln in fh if ln.strip()]


def _read_image_index(path: Path) -> List[Tuple[int, List[int]]]:
    """Parse ``image_index_<split>.txt`` -> list of (scene_id, [utt_indices])."""
    out: List[Tuple[int, List[int]]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n").strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                scene_id = int(parts[0])
                indices = ast.literal_eval(parts[1])
            else:
                # Fallback: line is the list itself; assign sequential ids
                indices = ast.literal_eval(parts[0])
                scene_id = len(out) + 1
            out.append((scene_id, list(indices)))
    return out


def _find_split_image_dir(
    raw_dir: Path, split: str, images_subdir: str = "images",
) -> Path:
    """Locate the per-split image folder. Tolerates several common layouts."""
    candidates = [
        raw_dir / images_subdir / split,        # data/raw/images/train/
        raw_dir / split,                        # data/raw/train/
        raw_dir / f"{split}_images",            # data/raw/train_images/
        raw_dir / images_subdir,                # flat (legacy)
    ]
    for c in candidates:
        if c.exists() and any(p.suffix.lower() in (".jpg", ".jpeg", ".png")
                              for p in c.iterdir()):
            return c
    return raw_dir / images_subdir / split  # default expected layout


def parse_msctd_split(
    raw_dir: Path,
    split: str,
    images_subdir: str = "images",
) -> pd.DataFrame:
    """Load one MSCTD split into a *utterance-level* DataFrame.

    Each scene contains 1..N utterances. Scene membership is dialogue
    context; each utterance still has its own image at
    ``<images_dir>/<split>/<utt_idx>.jpg``.
    """
    split = split.lower()
    eng = _read_indexed_lines(raw_dir / f"english_{split}.txt")
    sent = _read_indexed_lines(raw_dir / f"sentiment_{split}.txt")
    scenes = _read_image_index(raw_dir / f"image_index_{split}.txt")

    if len(eng) != len(sent):
        raise ValueError(
            f"MSCTD {split}: english ({len(eng)}) vs sentiment ({len(sent)}) "
            "length mismatch"
        )

    img_root = _find_split_image_dir(raw_dir, split, images_subdir)
    rows: List[Dict] = []
    for raw_scene_id, utt_indices in scenes:
        # Scene IDs restart from 1 in every split, so we prefix with the
        # source split to make them globally unique across the master CSV.
        scene_uid = f"{split}-{raw_scene_id}"
        for utt_idx in utt_indices:
            if utt_idx < 0 or utt_idx >= len(eng):
                continue
            try:
                label_id = int(sent[utt_idx].strip())
            except (ValueError, IndexError):
                continue
            if label_id not in _MSCTD_LABEL_TO_TEXT:
                continue
            # Each utterance has its own image: <split>/<utt_idx>.jpg
            img_path = img_root / f"{utt_idx}.jpg"
            rows.append({
                "sample_id": f"{split}-u{utt_idx:07d}",
                "image_path": str(img_path),
                "scene_id": scene_uid,
                "utterance_idx": utt_idx,
                "text": eng[utt_idx].strip(),
                "label_text": _MSCTD_LABEL_TO_TEXT[label_id],
                "label_id": label_id,
                "split": split,
            })
    return pd.DataFrame(rows)


def build_master_csv(
    raw_dir: Union[str, Path] = C.RAW_DIR,
    out_csv: Union[str, Path] = C.MASTER_CSV,
    restratify: bool = True,
    require_images: bool = False,
) -> pd.DataFrame:
    """Concatenate train/dev/test, optionally re-stratify into 70/15/15.

    Re-stratification is **scene-level** so dialogue context never crosses
    splits. When ``restratify=False`` we keep MSCTD's official splits,
    which are also scene-level by design.
    Set ``require_images=True`` to drop rows whose image is not on disk.
    """
    raw_dir = Path(raw_dir)
    parts = [parse_msctd_split(raw_dir, s) for s in ("train", "dev", "test")]
    df = pd.concat(parts, ignore_index=True)

    if require_images:
        df = df[df["image_path"].apply(lambda p: Path(p).exists())].reset_index(drop=True)

    if restratify:
        df = stratified_split(df, C.SPLIT.train, C.SPLIT.val, C.SPLIT.test, C.SPLIT.seed)

    # Reserve columns populated by the face-extraction stage
    df["num_faces"] = -1
    df["face_paths"] = "[]"

    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def dedupe_to_scenes(
    df: pd.DataFrame,
    label_col: str = "label_id",
) -> pd.DataFrame:
    """Reduce to one row per (split, scene_id) using the dominant label.

    Note: in MSCTD each *utterance* has its own image, so this function
    is a no-op for image-only training pipelines. It is kept for two
    use cases:

    * cross-checking that scene-level stratification did not leak;
    * downstream analyses that want one prediction per dialogue scene
      (e.g. averaging per-scene macro-F1).
    """
    def _mode(s: pd.Series) -> int:
        return int(s.value_counts().sort_index().idxmax())

    grouped = (
        df.groupby(["split", "scene_id"], as_index=False)
          .agg(label_id=(label_col, _mode),
               num_utterances=(label_col, "size"),
               image_path=("image_path", "first"))
    )
    grouped["label_text"] = grouped["label_id"].map(_MSCTD_LABEL_TO_TEXT)
    grouped["sample_id"] = grouped["scene_id"].astype(str)
    return grouped.reset_index(drop=True)


def stratified_split(
    df: pd.DataFrame,
    train_frac: float,
    val_frac: float,
    test_frac: float,
    seed: int,
    label_col: str = "label_id",
) -> pd.DataFrame:
    """Stratified scene-level 3-way split (no image leakage).

    We split *scenes*, not individual utterances: every utterance from the
    same dialogue scene ends up in the same split. Stratification is on the
    scene's dominant utterance label.
    """
    if abs((train_frac + val_frac + test_frac) - 1.0) > 1e-6:
        raise ValueError("train/val/test fractions must sum to 1")

    if "scene_id" not in df.columns:
        # Fallback to row-level stratification (legacy behaviour)
        train_df, temp_df = train_test_split(
            df, test_size=(val_frac + test_frac),
            stratify=df[label_col], random_state=seed,
        )
        rel_test = test_frac / (val_frac + test_frac)
        val_df, test_df = train_test_split(
            temp_df, test_size=rel_test,
            stratify=temp_df[label_col], random_state=seed,
        )
        return pd.concat([
            train_df.assign(split="train"),
            val_df.assign(split="val"),
            test_df.assign(split="test"),
        ], ignore_index=True)

    # Scene-level: dominant label per scene
    scene_label = (
        df.groupby("scene_id")[label_col]
          .agg(lambda s: int(s.value_counts().sort_index().idxmax()))
          .reset_index()
          .rename(columns={label_col: "_scene_label"})
    )
    train_scn, temp_scn = train_test_split(
        scene_label, test_size=(val_frac + test_frac),
        stratify=scene_label["_scene_label"], random_state=seed,
    )
    rel_test = test_frac / (val_frac + test_frac)
    val_scn, test_scn = train_test_split(
        temp_scn, test_size=rel_test,
        stratify=temp_scn["_scene_label"], random_state=seed,
    )
    assignments = pd.concat([
        train_scn.assign(_new_split="train"),
        val_scn.assign(_new_split="val"),
        test_scn.assign(_new_split="test"),
    ])[["scene_id", "_new_split"]]

    out = df.drop(columns=["split"], errors="ignore").merge(
        assignments, on="scene_id", how="inner",
    )
    out = out.rename(columns={"_new_split": "split"}).reset_index(drop=True)
    return out


def split_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a small table of class counts per split."""
    counts = (
        df.groupby(["split", "label_text"])
          .size().unstack(fill_value=0)
    )
    counts["total"] = counts.sum(axis=1)
    return counts.reset_index()


# -------------------------------------------------------------------------
# PyTorch Dataset classes
# -------------------------------------------------------------------------
class FullImageDataset(Dataset):
    """Returns (image_tensor, label_id, sample_id) for full-image models."""

    def __init__(
        self,
        df: pd.DataFrame,
        transform: Optional[Callable] = None,
        path_col: str = "image_path",
        label_col: str = "label_id",
        id_col: str = "sample_id",
    ) -> None:
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.path_col = path_col
        self.label_col = label_col
        self.id_col = id_col

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        img = Image.open(row[self.path_col]).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        label = int(row[self.label_col])
        return img, label, row[self.id_col]


class FaceDataset(Dataset):
    """One row == one face crop. Used to train the face-only model.

    Built from face_metadata.csv (one row per face). For images with
    multiple faces this naturally upsamples them, which we treat as data
    augmentation rather than leakage because each face is a different
    crop.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        transform: Optional[Callable] = None,
        path_col: str = "face_path",
        label_col: str = "label_id",
        id_col: str = "sample_id",
    ) -> None:
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.path_col = path_col
        self.label_col = label_col
        self.id_col = id_col

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        img = Image.open(row[self.path_col]).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        label = int(row[self.label_col])
        return img, label, row[self.id_col]


class MultimodalDataset(Dataset):
    """Returns (image_tensor, text_string, label_id, sample_id) for CLIP."""

    def __init__(
        self,
        df: pd.DataFrame,
        image_transform: Optional[Callable] = None,
        path_col: str = "image_path",
        text_col: str = "text",
        label_col: str = "label_id",
        id_col: str = "sample_id",
    ) -> None:
        self.df = df.reset_index(drop=True)
        self.image_transform = image_transform
        self.path_col = path_col
        self.text_col = text_col
        self.label_col = label_col
        self.id_col = id_col

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        img = Image.open(row[self.path_col]).convert("RGB")
        if self.image_transform is not None:
            img = self.image_transform(img)
        return img, str(row[self.text_col]), int(row[self.label_col]), row[self.id_col]


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def load_master(csv_path: Union[str, Path] = C.MASTER_CSV) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if "face_paths" in df.columns:
        df["face_paths"] = df["face_paths"].apply(_safe_literal_eval)
    return df


def load_face_metadata(csv_path: Union[str, Path] = C.FACE_METADATA_CSV) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def _safe_literal_eval(s):
    if isinstance(s, list):
        return s
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return []


def class_weights_from_df(
    df: pd.DataFrame, label_col: str = "label_id",
) -> torch.Tensor:
    """Inverse-frequency class weights (useful when classes are imbalanced)."""
    counts = df[label_col].value_counts().sort_index()
    n = counts.sum()
    weights = n / (len(counts) * counts.values.astype(float))
    return torch.tensor(weights, dtype=torch.float32)
