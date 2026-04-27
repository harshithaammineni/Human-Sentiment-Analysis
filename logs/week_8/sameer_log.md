# Weekly Training Log

**Name:** Shaik Sameer
**Student ID:** 6944091
**Week:** Week 8 (06-04-2026 to 12-04-2026)

---

## Tasks completed
- [x] Helped Harshitha integrate the new `face_metadata.csv` back into the master CSV via `src/dataset.py::load_face_metadata` (added the join + sanity check).
- [x] Refactored `src/utils.py::seed_everything(42)` so every notebook calls the same global seeder — this was the source of two reproducibility bugs Ravi Teja hit while debugging the head training.
- [x] Wrote `outputs/tables/dataset_split_summary.csv` exporter and added it as a side-effect of cell 4 of Notebook 01.
- [x] Reviewed and merged the `face-model`, `aug-robust`, `full-image` and `clip-multimodal` PRs into `main`.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `c8d9e0f` | `data-prep` | data: load_face_metadata join + assertions | src/dataset.py |
| `1a2b3c4` | `data-prep` | data: dataset_split_summary.csv exporter in NB01 | notebooks/01_dataset_preparation.ipynb |
| `d5e6f7a` | `main` | utils: single seed_everything() entry point | src/utils.py |
| `8b9c0d1` | `main` | logs(week_8): sameer - data plumbing, seeding, PR reviews | logs/week_8/sameer_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Re-run majority baseline on the matched test split (post face-extract) | `src/eval.py::majority_baseline` | always-predict-neutral | acc 0.379, macro-F1 0.183 (unchanged — sanity check passed) |

## Hyperparameters tested
- learning rate: n/a
- batch size: n/a
- epochs: n/a
- other: confirmed seed=42 propagates into PyTorch, NumPy, Python `random`, and the dataloaders.

## Results / metrics
- accuracy: 0.379 (baseline only)
- macro F1: 0.183
- weighted F1: 0.209
- notes: no training, but I needed to lock in the test-set indices before everyone trained against them, so the "did the split move?" check is a real sanity check.

## Problems found
- Two notebooks were doing their own `random.seed(42)` and `torch.manual_seed(42)` differently, leading to subtly different DataLoader shuffles between runs.
- The `face_detected_flag` join was producing NaN rows for 14 images that Harshitha had filtered out.

## Fixes made
- Centralised seeding in `src/utils.py::seed_everything` and replaced the per-notebook copies.
- Filled the missing flags with 0 and added an assertion in `load_face_metadata` that there are zero NaN rows post-join.

## Observations / insights
- The repo is now stable enough that all four downstream notebooks can run end-to-end without anyone touching anyone else's branches.
- We should keep the predictions CSVs (face + full-image) in `outputs/predictions/` and *never* regenerate them inside Notebook 06 unless the upstream model retrains.

## Tasks for next week
- [ ] Help Sai Teja check his Experiment B/C numbers against the same test-set indices.
- [ ] Update `README.md` with the actual run order once everyone's notebooks land.
