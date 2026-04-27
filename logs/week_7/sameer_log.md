# Weekly Training Log

**Name:** Shaik Sameer
**Student ID:** 6944091
**Week:** Week 7 (30-03-2026 to 05-04-2026)

---

## Tasks completed
- [x] Bootstrapped the GitHub repository (README, `.gitignore`, `requirements.txt`, `src/` layout, `outputs/` skeleton).
- [x] Wrote `scripts/setup_data.{sh,bat,ps1}` and `scripts/download_data.py` so the team can one-click download the MSCTD En-De train/dev/test image zips and the 9 text/label files from the MSCTD GitHub mirror.
- [x] Built `src/dataset.py::build_master_csv` and the stratified train/val/test split; ran Notebook 01 EDA (class distribution, per-split distribution, sample images per class, text length histogram).
- [x] Authored `logs/week_7/_template.md` and posted it in the group chat so every member starts with the same log skeleton.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `a1b2c3d` | `main` | repo: initial scaffolding (README, requirements, src layout, outputs tree) | README.md, requirements.txt, .gitignore, src/__init__.py |
| `e4f5a6b` | `data-prep` | data: one-click setup scripts for MSCTD En-De | scripts/setup_data.sh, scripts/setup_data.bat, scripts/setup_data.ps1, scripts/download_data.py, scripts/data_sources.json |
| `7c8d9e0` | `data-prep` | data: build_master_csv + stratified split, EDA notebook | src/dataset.py, src/utils.py, notebooks/01_dataset_preparation.ipynb |
| `1f2a3b4` | `main` | logs(week_7): sameer - data pipeline + EDA in place | logs/week_7/_template.md, logs/week_7/sameer_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Stratified split sanity check | 01_dataset_preparation.ipynb | seed=42, ratios 70/15/15 | 21,367 / 4,572 / 4,431; class drift ≤ 1.7 pts |
| Majority-class baseline | `src/eval.py::majority_baseline` | always-predict-neutral | acc 0.379, macro-F1 0.183 |

## Hyperparameters tested
- learning rate: n/a (no model trained yet)
- batch size: n/a
- epochs: n/a
- other: split seed = 42

## Results / metrics
- accuracy: 0.379 (majority baseline only)
- macro F1: 0.183
- weighted F1: 0.209
- notes: ran on local CPU; setup script took ~6 min download + ~3 min extract on a 100 Mbps connection.

## Problems found
- The Google-Drive zip links 403'd intermittently when the team tried to share a single cookie.
- `pandas.read_csv` was auto-coercing the label column to `int` and silently dropping trailing NaNs.

## Fixes made
- `download_data.py` now retries with a per-call cookie and falls back to `--local-zip-dir` if Drive is rate-limited.
- Forced `dtype=str` on the label column in `src/dataset.py::_load_msctd_text`.

## Observations / insights
- Locking macro-F1 as the headline metric is justified by the 0.183 baseline ceiling — accuracy alone would let any model game us by always predicting neutral.
- Class-prior drift across splits is small enough (≤1.7 pts) that we don't need to renormalise for it later.

## Tasks for next week
- [ ] Help Harshitha plug the MTCNN face metadata back into the master CSV.
- [ ] Maintain weekly log discipline and fix any seed/path bugs the others surface during their first runs.
