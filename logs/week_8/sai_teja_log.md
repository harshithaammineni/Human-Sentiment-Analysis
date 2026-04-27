# Weekly Training Log

**Name:** Tharigopula Sai Teja
**Student ID:** 6945944
**Week:** Week 8 (06-04-2026 to 12-04-2026)

---

## Tasks completed
- [x] Built `src/transforms.py::make_degradation` final implementation across the three families (frequency / spatial / brightness).
- [x] Materialised the degraded test set on disk under `data/degraded_faces/test/` so Harshitha and I can both inspect the same crops, and so the fusion model can re-use them later if needed.
- [x] Notebook 04 cell 1: visualised one example per family on `outputs/plots/augmentation_examples.png` and confirmed by eye that the degraded faces are still humanly classifiable.
- [x] Coordinated with Harshitha so we share the same `(image_id, face_id)` key between the original and degraded face CSVs.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `2e3f4a5` | `aug-robust` | aug: final make_degradation across frequency/spatial/brightness | src/transforms.py |
| `6b7c8d0` | `aug-robust` | aug: materialise degraded test set + visualisation cell | notebooks/04_augmentation_robustness.ipynb |
| `e1f2a3b` | `main` | logs(week_8): sai-teja - degradation toolkit + degraded test set | logs/week_8/sai_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Materialise `data/degraded_faces/test/` | NB 04 cell 2 | one random family per crop, seeded | 6,564 degraded crops generated, 1:1 with originals |

## Hyperparameters tested
- learning rate: n/a (no training yet)
- batch size: n/a
- epochs: n/a
- other: degradation strengths kept identical to Week 7 — sigma_blur=2, noise_std=0.05, gamma in [0.5, 1.5], affine ±10°.

## Results / metrics
- accuracy: n/a (no model trained this week)
- macro F1: n/a
- weighted F1: n/a
- notes: degraded set is ~340 MB on disk, excluded from git via `.gitignore`.

## Problems found
- The first version of `mixed_train_transform` was applying degradation *before* normalisation, which interacted badly with `ColorJitter`'s gamma path (saturation bug at low gamma).
- Random seeds inside `make_degradation` were drifting between dataloader workers, so two workers sometimes degraded the same image differently between epochs.

## Fixes made
- Re-ordered the pipeline: degradation happens on the PIL image, *then* normalisation. Verified visually.
- Switched to a per-sample seed derived from `(image_id, epoch)` so degradation is deterministic across workers — a correctness fix, not just cosmetic.

## Observations / insights
- The degraded test set is a small enough disk hit (~340 MB) that we can keep it materialised; this is much faster than re-degrading per epoch when running Experiment B.
- "Frequency" degradations look the worst by eye on the face crops — happiness/anger cues in the eyes and mouth corners get washed out the most.

## Tasks for next week
- [ ] Run Experiment A / B / C in Notebook 04 once Harshitha hands me the original-trained checkpoint.
- [ ] Ship `outputs/metrics/robustness_results.csv` with all four cells.
