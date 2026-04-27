"""Face extraction pipeline using facenet-pytorch's MTCNN.

Reads ``data/processed/msctd_master.csv``, runs MTCNN on every image,
crops + resizes faces to ``FACE_SIZE`` and saves them under
``data/faces/<sample_id>__face<k>.jpg``. Produces:

  * ``data/processed/face_metadata.csv`` -- one row per detected face
    (used to train the face model)
  * Updated ``msctd_master.csv`` with ``num_faces`` and ``face_paths``
    columns (used by the fusion model).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageDraw
from tqdm.auto import tqdm

from . import config as C
from .utils import get_device


# -------------------------------------------------------------------------
# MTCNN wrapper
# -------------------------------------------------------------------------
class FaceExtractor:
    """Thin wrapper around facenet-pytorch MTCNN with sensible defaults."""

    def __init__(
        self,
        image_size: int = C.FACE_SIZE[0],
        margin: int = 20,
        min_face_size: int = 40,
        thresholds: Tuple[float, float, float] = (0.6, 0.7, 0.7),
        device: Optional[torch.device] = None,
    ) -> None:
        from facenet_pytorch import MTCNN  # local import keeps test envs light

        self.device = device or get_device()
        # keep_all=True so we get every detected face, not just the most prominent
        self.mtcnn = MTCNN(
            image_size=image_size,
            margin=margin,
            min_face_size=min_face_size,
            thresholds=list(thresholds),
            keep_all=True,
            post_process=False,  # we re-normalise downstream in transforms.py
            device=str(self.device),
        )
        self.image_size = image_size

    @torch.no_grad()
    def detect(
        self, image: Image.Image,
    ) -> Tuple[List[Image.Image], List[float], Optional[np.ndarray]]:
        """Return (face_pil_crops, confidences, boxes) for one PIL image."""
        # MTCNN.detect returns boxes (Nx4) and probs; .extract returns aligned crops.
        boxes, probs = self.mtcnn.detect(image)
        if boxes is None or len(boxes) == 0:
            return [], [], None

        # Use the built-in cropper to keep size/margin consistent.
        face_tensors = self.mtcnn.extract(image, boxes, save_path=None)
        if face_tensors is None:
            return [], [], boxes
        if face_tensors.ndim == 3:
            face_tensors = face_tensors.unsqueeze(0)

        crops: List[Image.Image] = []
        for ft in face_tensors:
            arr = ft.detach().cpu().permute(1, 2, 0).numpy()
            arr = np.clip(arr, 0, 255).astype(np.uint8)
            crops.append(Image.fromarray(arr))

        confs = [float(p) if p is not None else 0.0 for p in probs]
        return crops, confs, boxes


# -------------------------------------------------------------------------
# Batch driver
# -------------------------------------------------------------------------
def run_extraction(
    master_df: pd.DataFrame,
    out_dir: Union[str, Path] = C.FACES_DIR,
    extractor: Optional[FaceExtractor] = None,
    overwrite: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Detect faces for every row of ``master_df``.

    Returns
    -------
    updated_master : DataFrame
        Same as input but with ``num_faces`` and ``face_paths`` filled.
    face_metadata : DataFrame
        One row per detected face (used to train the face model).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    extractor = extractor or FaceExtractor()

    face_rows: List[dict] = []
    num_faces_col: List[int] = []
    face_paths_col: List[List[str]] = []

    iterator = tqdm(master_df.itertuples(index=False), total=len(master_df), desc="MTCNN")
    for row in iterator:
        sample_id = row.sample_id
        img_path = row.image_path
        try:
            img = Image.open(img_path).convert("RGB")
        except Exception:
            num_faces_col.append(0)
            face_paths_col.append([])
            continue

        crops, confs, _ = extractor.detect(img)
        paths_for_row: List[str] = []
        for k, (crop, conf) in enumerate(zip(crops, confs)):
            face_path = out_dir / f"{sample_id}__face{k}.jpg"
            if overwrite or not face_path.exists():
                crop.save(face_path, format="JPEG", quality=92)
            paths_for_row.append(str(face_path))
            face_rows.append({
                "sample_id": sample_id,
                "face_index": k,
                "face_path": str(face_path),
                "image_path": img_path,
                "detection_confidence": conf,
                "label_id": int(row.label_id),
                "label_text": row.label_text,
                "split": row.split,
            })

        num_faces_col.append(len(crops))
        face_paths_col.append(paths_for_row)

    updated_master = master_df.copy()
    updated_master["num_faces"] = num_faces_col
    updated_master["face_paths"] = [str(p) for p in face_paths_col]

    face_metadata = pd.DataFrame(face_rows)
    return updated_master, face_metadata


# -------------------------------------------------------------------------
# Visual sanity check
# -------------------------------------------------------------------------
def visualise_detection(
    image_path: Union[str, Path],
    extractor: Optional[FaceExtractor] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> Image.Image:
    """Draw MTCNN bounding boxes on a single image and optionally save."""
    extractor = extractor or FaceExtractor()
    img = Image.open(image_path).convert("RGB")
    _, _, boxes = extractor.detect(img)
    if boxes is not None:
        draw = ImageDraw.Draw(img)
        for box in boxes:
            draw.rectangle(list(box), outline="red", width=3)
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(save_path)
    return img
