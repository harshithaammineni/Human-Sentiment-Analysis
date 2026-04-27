"""Download and lay out the MSCTD English-German dataset under ``data/raw/``.

What this script does, in order:

1. Clones the public MSCTD repository (https://github.com/XL2248/MSCTD)
   into a temp directory, then copies the ``ende/`` text/label files
   (english_*.txt, image_index_*.txt, sentiment_*.txt) into ``data/raw/``.

2. Downloads the image archives from Google Drive using ``gdown`` and
   extracts them into ``data/raw/images/``. The Google Drive file IDs
   are taken from the ``--config`` JSON, or from CLI flags, or from
   environment variables -- whichever you prefer.

3. Verifies the final layout: 9 .txt files and a non-empty ``images/``
   folder whose filenames cover the ones referenced by ``image_index_*``.

You can rerun the script safely; existing files are skipped unless
``--force`` is passed.

Usage examples
--------------
# All three image archives in one go (Google Drive file IDs from MSCTD README):
python scripts/download_data.py \\
    --train-id <FILE_ID> --dev-id <FILE_ID> --test-id <FILE_ID>

# Or point at a JSON config:
python scripts/download_data.py --config scripts/data_sources.json

# If you already downloaded the zips manually, point at the folder
# containing them (filenames must contain 'train', 'dev' or 'test'):
python scripts/download_data.py --local-zip-dir /path/to/zips

# Skip the image step entirely (txt files only):
python scripts/download_data.py --skip-images

# Just verify the current layout:
python scripts/download_data.py --verify-only
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Optional


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
IMAGES_DIR = DATA_RAW / "images"

MSCTD_REPO = "https://github.com/XL2248/MSCTD.git"
MSCTD_ENDE_SUBDIR = "MSCTD_data/ende"

EXPECTED_TXT = [
    "english_train.txt", "english_dev.txt", "english_test.txt",
    "image_index_train.txt", "image_index_dev.txt", "image_index_test.txt",
    "sentiment_train.txt", "sentiment_dev.txt", "sentiment_test.txt",
]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def log(msg: str) -> None:
    print(f"[download_data] {msg}", flush=True)


def ensure_dirs() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], check: bool = True) -> None:
    log(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# ---------------------------------------------------------------------
# Step 1: text/label files via git clone
# ---------------------------------------------------------------------
def fetch_text_files(force: bool = False) -> None:
    missing = [f for f in EXPECTED_TXT if not (DATA_RAW / f).exists()]
    if not missing and not force:
        log("All 9 text files already in data/raw/, skipping git clone.")
        return

    if not have("git"):
        raise SystemExit(
            "git is required to clone the MSCTD repo. Install git or download "
            "the txt files manually from https://github.com/XL2248/MSCTD."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir) / "MSCTD"
        run(["git", "clone", "--depth", "1", MSCTD_REPO, str(tmp)])
        src_dir = tmp / MSCTD_ENDE_SUBDIR
        if not src_dir.exists():
            # Fall back: scan the cloned repo for the files (paths can change)
            src_dir = _find_ende_dir(tmp)
        if src_dir is None or not src_dir.exists():
            raise SystemExit(
                f"Could not locate {MSCTD_ENDE_SUBDIR} in the cloned MSCTD repo. "
                "Check the repo layout and update MSCTD_ENDE_SUBDIR."
            )
        for fn in EXPECTED_TXT:
            src = src_dir / fn
            dst = DATA_RAW / fn
            if not src.exists():
                log(f"WARNING: {fn} not found in repo at {src}")
                continue
            if dst.exists() and not force:
                continue
            shutil.copy2(src, dst)
            log(f"copied {fn}")


def _find_ende_dir(repo_root: Path) -> Optional[Path]:
    """Best-effort search in case the repo layout differs from MSCTD_data/ende."""
    for p in repo_root.rglob("english_train.txt"):
        return p.parent
    return None


# ---------------------------------------------------------------------
# Step 2: image archives via gdown (or local zips)
# ---------------------------------------------------------------------
def fetch_images(
    train_id: Optional[str],
    dev_id: Optional[str],
    test_id: Optional[str],
    local_zip_dir: Optional[Path],
    force: bool = False,
) -> None:
    """Either download from Google Drive or extract local zips."""
    if local_zip_dir is not None:
        zips = _collect_local_zips(local_zip_dir)
        if not zips:
            raise SystemExit(f"No .zip files found in {local_zip_dir}")
        log(f"Using local zips: {[z.name for z in zips]}")
        for z in zips:
            _extract_zip(z)
        return

    ids = {"train": train_id, "dev": dev_id, "test": test_id}
    missing = [k for k, v in ids.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing Google Drive file IDs for: {missing}. "
            "Open https://github.com/XL2248/MSCTD , find the En-De image "
            "links in the README, and pass the IDs via --train-id / --dev-id "
            "/ --test-id, or via a --config JSON, or set environment vars "
            "MSCTD_TRAIN_ID, MSCTD_DEV_ID, MSCTD_TEST_ID."
        )

    _ensure_gdown()
    import gdown  # type: ignore

    for split, file_id in ids.items():
        out_zip = DATA_RAW / f"msctd_ende_{split}.zip"
        if out_zip.exists() and not force:
            log(f"already downloaded: {out_zip.name}")
        else:
            log(f"downloading {split} images via gdown (id={file_id}) ...")
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, str(out_zip), quiet=False)
        _extract_zip(out_zip)


def _ensure_gdown() -> None:
    try:
        import gdown  # noqa: F401
    except ImportError:
        log("gdown not installed -- installing now")
        run([sys.executable, "-m", "pip", "install", "gdown"])


def _collect_local_zips(folder: Path) -> list[Path]:
    out = []
    for p in sorted(folder.glob("*.zip")):
        n = p.name.lower()
        if any(k in n for k in ("train", "dev", "test")):
            out.append(p)
    return out


def _split_from_name(name: str) -> Optional[str]:
    """Best-effort detection of which split a zip filename belongs to."""
    n = name.lower()
    for k in ("train", "dev", "test"):
        if k in n:
            return k
    return None


def _extract_zip(zip_path: Path) -> None:
    """Extract a per-split image zip into ``images/<split>/``.

    Train, dev and test scene IDs collide (each starts at 1), so we keep
    them in separate subfolders rather than flattening into ``images/``.
    """
    split = _split_from_name(zip_path.name)
    if split is None:
        log(f"could not infer split from filename {zip_path.name}; "
            f"extracting flat into {IMAGES_DIR}")
        target_root = IMAGES_DIR
    else:
        target_root = IMAGES_DIR / split
    target_root.mkdir(parents=True, exist_ok=True)
    log(f"extracting {zip_path.name} -> {target_root}")

    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            # Flatten leading folder components (some zips wrap in 'train/'
            # or '<split>_images/') so files land directly in target_root.
            target = target_root / Path(member).name
            if target.exists():
                continue
            with zf.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)


# ---------------------------------------------------------------------
# Step 3: verify
# ---------------------------------------------------------------------
def verify_layout(strict: bool = False) -> bool:
    ok = True
    log(f"verifying {DATA_RAW}")
    for fn in EXPECTED_TXT:
        p = DATA_RAW / fn
        if not p.exists():
            log(f"MISSING: {fn}")
            ok = False
        else:
            n = sum(1 for _ in open(p, "r", encoding="utf-8"))
            log(f"  {fn}: {n} lines")

    # Count images per split (recursively in case of nested layout)
    total = 0
    for split in ("train", "dev", "test"):
        n = sum(1 for _ in (IMAGES_DIR / split).rglob("*.jpg")) if (IMAGES_DIR / split).exists() else 0
        total += n
        log(f"  images/{split}/: {n} .jpg files")
    if total == 0:
        log("MISSING: no images in data/raw/images/")
        ok = False

    if ok and strict:
        ok = _cross_check_image_index() and ok

    log("LAYOUT OK" if ok else "LAYOUT INCOMPLETE")
    return ok


def _parse_image_index_utt_indices(path: Path) -> list[int]:
    """Parse ``<scene_id>\\t[utt_idx, ...]`` and flatten to all utt indices."""
    import ast as _ast
    out: list[int] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\r\n").strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            payload = parts[1] if len(parts) == 2 else parts[0]
            try:
                out.extend(int(x) for x in _ast.literal_eval(payload))
            except (ValueError, SyntaxError):
                continue
    return out


def _cross_check_image_index() -> bool:
    """Each utterance has its own image at ``<split>/<utt_idx>.jpg`` -- check
    every utterance index referenced by ``image_index_<split>.txt`` exists.
    """
    ok = True
    for split in ("train", "dev", "test"):
        idx_path = DATA_RAW / f"image_index_{split}.txt"
        if not idx_path.exists():
            continue
        utt_indices = _parse_image_index_utt_indices(idx_path)
        split_dir = IMAGES_DIR / split
        missing = [u for u in utt_indices if not (split_dir / f"{u}.jpg").exists()]
        if missing:
            ok = False
            log(f"{split}: {len(missing)}/{len(utt_indices)} images missing on disk. "
                f"first few utt indices -> {missing[:10]}")
        else:
            log(f"{split}: all {len(utt_indices)} referenced images present")
    return ok


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--train-id", default=os.environ.get("MSCTD_TRAIN_ID"),
                   help="Google Drive file ID for the train images zip")
    p.add_argument("--dev-id", default=os.environ.get("MSCTD_DEV_ID"),
                   help="Google Drive file ID for the dev images zip")
    p.add_argument("--test-id", default=os.environ.get("MSCTD_TEST_ID"),
                   help="Google Drive file ID for the test images zip")
    p.add_argument("--config", type=Path, default=None,
                   help="JSON file with keys train/dev/test mapping to file IDs")
    p.add_argument("--local-zip-dir", type=Path, default=None,
                   help="Folder containing already-downloaded image zips")
    p.add_argument("--skip-text", action="store_true",
                   help="Skip cloning MSCTD for the txt/label files")
    p.add_argument("--skip-images", action="store_true",
                   help="Skip the image download/extract step")
    p.add_argument("--verify-only", action="store_true",
                   help="Only verify the current data/raw/ layout")
    p.add_argument("--strict-verify", action="store_true",
                   help="Cross-check filenames in image_index_*.txt against disk")
    p.add_argument("--force", action="store_true",
                   help="Re-download / overwrite even if files exist")
    return p.parse_args()


def merge_config(args: argparse.Namespace) -> Dict[str, Optional[str]]:
    ids = {"train": args.train_id, "dev": args.dev_id, "test": args.test_id}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        for k in ("train", "dev", "test"):
            if not ids[k] and cfg.get(k):
                ids[k] = cfg[k]
    return ids


def main() -> int:
    args = parse_args()
    ensure_dirs()

    if args.verify_only:
        return 0 if verify_layout(strict=args.strict_verify) else 1

    if not args.skip_text:
        fetch_text_files(force=args.force)

    if not args.skip_images:
        ids = merge_config(args)
        fetch_images(
            train_id=ids["train"], dev_id=ids["dev"], test_id=ids["test"],
            local_zip_dir=args.local_zip_dir, force=args.force,
        )

    ok = verify_layout(strict=args.strict_verify)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
