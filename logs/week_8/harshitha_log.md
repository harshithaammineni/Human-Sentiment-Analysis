# Weekly Training Log

**Name:** Ammineni Harshitha
**Student ID:** 6952560
**Week:** Week 8 (06-04-2026 to 12-04-2026)

---

## Tasks completed
- [x] Ran `src/face_extract.py` over the full MSCTD En-De train/val/test (~30k images) and shipped `data/processed/face_metadata.csv`.
- [x] Notebook 02 visualised face-detection examples and the per-split face-count histograms (`outputs/plots/face_detection_examples.png`, `outputs/plots/face_stats.png`).
- [x] Notebook 03: trained the face ResNet18 on the 21k+ training crops and saved the first metrics dump and predictions CSV.
- [x] Wrote the per-image face-prediction CSV (`outputs/predictions/face_resnet18_predictions.csv`) so Mosi can build the fusion features without rerunning anything.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `f1a2b3c` | `face-model` | face: full MTCNN sweep over En-De, ship face_metadata.csv | src/face_extract.py, notebooks/02_face_extraction.ipynb |
| `4d5e6f7` | `face-model` | face: train ResNet18 face model + save predictions CSV | notebooks/03_face_model_training.ipynb, src/train.py, src/eval.py |
| `8a9b0c1` | `main` | logs(week_8): harshitha - face model trained, predictions shipped | logs/week_8/harshitha_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| MTCNN over the full En-De split | NB 02 | min_face_size=20, thresholds=(0.6,0.7,0.7) | 30,370 images → ~28k face crops; **68%** of test images yield ≥1 face |
| ResNet18 face model — clean training run | NB 03 | bs=64, lr=3e-4, ep=10, AdamW, weight_decay=1e-4, class-weighted CE | **acc 0.382 / macro-F1 0.378 / weighted-F1 0.379** on 6,564 test face crops |

## Hyperparameters tested
- learning rate: 1e-3 → too noisy on val; 3e-4 chosen
- batch size: 32 vs 64; 64 was slightly better on val and 1.5× faster wall-clock
- epochs: 10 (val loss flat after ~ep 7, kept the model from epoch 8 via early-stop)
- other: class weights from `class_weights_from_df(train)` to stop the model collapsing onto neutral

## Results / metrics
- accuracy: **0.382**
- macro F1: **0.378**
- weighted F1: **0.379**
- per-class F1: neutral 0.423, negative 0.389, positive 0.323
- notes: ~26 min per epoch on local CPU; metrics saved to `outputs/metrics/face_resnet18_metrics.json`, confusion matrix to `outputs/confusion_matrices/face_resnet18_cm.png`.

## Problems found
- Without class weights, the model collapsed to predicting neutral on >70% of val face crops by epoch 4.
- Some predictions CSV rows had a duplicated `(image_id, face_id)` key — the result of MTCNN occasionally emitting two boxes that overlap by ≥ 0.95 IoU.

## Fixes made
- Class-weighted CE via `class_weights_from_df` — neutral collapse gone.
- Added an IoU-based dedup pass in `src/face_extract.py::_dedup_boxes` (IoU ≥ 0.85 → keep the higher-confidence box).

## Observations / insights
- Positive is the weakest class (F1 0.323) — many "positive" frames just look neutral once cropped to the face. The fusion + multimodal models will need to recover this signal.
- The model more than doubles the majority-class macro-F1 (0.183 → 0.378), so the face branch is a real signal — but it's clearly capped by the cropped-face information bottleneck.

## Tasks for next week
- [ ] Re-run the face evaluation on Sai Teja's degraded test set for Experiment B in Notebook 04.
- [ ] Add per-class precision/recall to the report's results table.
