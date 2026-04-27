# Weekly Training Log

**Name:** Shaik Sameer
**Student ID:** 6944091
**Week:** Week 9 (13-04-2026 to 19-04-2026)

---

## Tasks completed
- [x] Refactored `src/train.py` to accept class weights through a single `class_weights=` argument (was previously plumbed inconsistently between Notebook 03 and Notebook 05).
- [x] Added `outputs/tables/` exporters to Notebook 04 and Notebook 06 so every results table the report needs is regenerated automatically.
- [x] Wrote `run_instructions.md` with the canonical 01→07 run order, the seed contract and the "fast path" notes Mosi needs in Notebook 06.
- [x] Reviewed and merged Sai Teja's `aug-robust` and Mosi's `fusion` PRs.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `3d4e5f6` | `main` | train: unify class_weights argument across NB03/NB05 | src/train.py |
| `7a8b9c0` | `main` | docs: run_instructions.md (run order, seeds, fast-path) | run_instructions.md |
| `d1e2f3a` | `data-prep` | tables: dataset_split_summary + final_model_comparison exporters | notebooks/04_augmentation_robustness.ipynb, notebooks/06_fusion_model.ipynb |
| `4b5c6d7` | `main` | logs(week_9): sameer - run instructions + table plumbing | logs/week_9/sameer_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| End-to-end re-run of NB 01 → NB 06 from a clean checkout | full pipeline | seed=42, defaults | All notebooks run top-to-bottom without manual intervention; tables match the per-notebook metrics JSONs |

## Hyperparameters tested
- learning rate: n/a (no model trained this week)
- batch size: n/a
- epochs: n/a
- other: confirmed `seed_everything(42)` reproduces Harshitha's and Ravi Teja's metrics to 4 decimal places.

## Results / metrics
- accuracy: pipeline acceptance — all 4 model metrics match the prior week's runs exactly
- macro F1: same
- weighted F1: same
- notes: full pipeline (no caches, no checkpoints) takes ~6 hours on local CPU; with cached checkpoints and predictions, it's ~25 min.

## Problems found
- One notebook was importing `from src.train import train` and another `from src import train as train_module` — divergent. This is the kind of thing that breaks Colab kernels at the worst possible time.
- The fusion-table column order was sensitive to dict insertion order between Python versions.

## Fixes made
- Standardised to `from src.train import train_classifier`.
- Fusion table is now built via `pd.DataFrame(rows, columns=FUSION_FEATURE_COLS)` with `FUSION_FEATURE_COLS` as a single source of truth in `src/fusion.py`.

## Observations / insights
- The "fast path" cell in Notebook 06 (skip cells 3 + 4 if the cached predictions exist) is going to be a lifesaver during the report-writing week — full re-runs aren't necessary and we don't accidentally retrain anything.
- We are now in good shape on reproducibility; nothing in `outputs/` is hand-edited.

## Tasks for next week
- [ ] Lock the README + `run_instructions.md` final wording.
- [ ] Help Mosi cross-check the final comparison table the night before the deadline.
