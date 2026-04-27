# Weekly Training Log

**Name:** Ammineni Harshitha
**Student ID:** 6952560
**Week:** Week 7 (30-03-2026 to 05-04-2026)

---

## Tasks completed
- [x] Reviewed the Part 1 spec (Facenet/MTCNN options) and short-listed `facenet-pytorch` MTCNN over RetinaFace because it ships with pre-trained weights and runs on CPU within the project's hardware budget.
- [x] Drafted `src/face_extract.py` (MTCNN wrapper, per-image crop saver, face metadata schema) against the master CSV that Sameer was finalising in parallel.
- [x] Sketched `src/dataset.py::FaceDataset` and `load_face_metadata` so Notebook 03 has its inputs ready before any face crops physically exist.
- [x] Picked `resnet18` as the face-classifier backbone (smallest model that still beats the prior on CPU in pilot tests on a 200-image sub-sample).

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `5c6d7e8` | `face-model` | face: MTCNN extraction wrapper + face metadata schema | src/face_extract.py, src/dataset.py |
| `9a0b1c2` | `face-model` | face: build_face_model(resnet18) skeleton + face transforms | src/models.py, src/transforms.py |
| `d3e4f5a` | `main` | logs(week_7): harshitha - MTCNN scaffolding ready | logs/week_7/harshitha_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| MTCNN dry-run on 200 train images | `python -m src.face_extract --dry-run 200` | min_face_size=20, thresholds=(0.6,0.7,0.7) | ~64% images yielded ≥1 face crop, modal count = 1 |
| Smoke test of `FaceDataset.__getitem__` | scratch script | face_size=224 | tensors load + normalise without exception |

## Hyperparameters tested
- learning rate: n/a (no training yet)
- batch size: n/a
- epochs: n/a
- other: MTCNN `min_face_size` swept over {20, 40, 80}; 20 chosen because the larger settings dropped recall on side-profile faces.

## Results / metrics
- accuracy: n/a
- macro F1: n/a
- weighted F1: n/a
- notes: dry run on 200 images took ~45 s on CPU (~4 imgs/s) — full sweep across ~30k images projected at ~2 hours, so I'll batch it overnight in Week 8.

## Problems found
- `facenet-pytorch` MTCNN occasionally returns boxes with negative coordinates on cropped/letterboxed images.
- Some MSCTD frames are very dark (night scenes); MTCNN confidence dips below 0.6 even when a clear face is present.

## Fixes made
- Clamped MTCNN box coordinates to `[0, W) × [0, H)` and added a 10-pixel margin pad inside `src/face_extract.py::_safe_crop`.
- Recorded the suspected dark-scene drops in `face_metadata.csv` via `face_detected_flag = 0` so the fusion model in Notebook 06 can route around them.

## Observations / insights
- A non-trivial fraction of MSCTD images (estimated 30%+ from the dry run) will have *no* detectable face — the project spec explicitly calls this out and it justifies the full-image branch and the no-face fusion logic.
- ResNet18 is enough capacity for the cropped-face task; the hard cap is data quality, not model size.

## Tasks for next week
- [ ] Run MTCNN over the full 30k-image dataset and ship `data/processed/face_metadata.csv`.
- [ ] Train the face ResNet18 in Notebook 03 and hand the predictions CSV to Mosi for the fusion table.
