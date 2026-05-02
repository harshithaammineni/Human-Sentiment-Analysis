# Weekly Training Log

**Name:** Shaik Sameer
**Student ID:** 6944091
**Week:** Week 10 (20-04-2026 to 26-04-2026)

---

## Tasks completed
- [x] Cross-checked the final `outputs/tables/final_model_comparison.csv` against every per-model `outputs/metrics/*_metrics.json` — all rows match to 4 decimal places.
- [x] Updated `README.md` with the final pipeline diagram, run order and group-member focus table.
- [x] Wrote the abstract and the introduction draft for the report.
- [x] Final pre-submission housekeeping: gitignore audit, output cleanup, last log commit per member.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `5f6a7b9` | `main` | docs: final README with pipeline diagram + member focus | README.md |
| `0c1d2e3` | `report` | report: abstract + introduction draft | report/main.tex, report/sections/01_intro.tex |
| `4f5a6c7` | `main` | tables: cross-check final_model_comparison vs per-model JSONs | outputs/tables/final_model_comparison.csv |
| `8d9e0f1` | `main` | logs(week_10): sameer - submission housekeeping | logs/week_10/sameer_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Comparison-table cross-check | NB 06 + JSON cross-walk | n/a | every model's `accuracy/macro_f1/weighted_f1` matches its per-model JSON exactly |

## Hyperparameters tested
- learning rate: n/a
- batch size: n/a
- epochs: n/a
- other: confirmed `seed_everything(42)` reproduces the final table on a fresh checkout.

## Results / metrics
- accuracy: pipeline-level acceptance
- macro F1: same — all per-model numbers stable across re-runs
- weighted F1: same
- notes: the final table now shows majority baseline (0.183), face (0.378), face on degraded (0.322), face aug (0.366), full-image (0.362), fusion (0.357), CLIP multimodal (0.562). The CLIP row was Mosi's contribution this week.

## Problems found
- Two `outputs/predictions/*.csv` files were not in `.gitignore` and were ~50 MB each.
- The IEEE template's `\bibliography{}` was throwing a missing-`.bbl` warning on the first compile.

## Fixes made
- Added `outputs/predictions/*.csv` to `.gitignore` and removed them from the index.
- Wired up `bibtex` into the report build instructions and verified `make report` works end-to-end.

## Observations / insights
- The "logical fusion" + "stability" criteria from the project spec are clearly satisfied by Mosi's CLIP run — the final macro-F1 (0.562) is ~50% above the best unimodal model (0.378) and there were no NaN/crash incidents.
- Every notebook now runs from a clean checkout end-to-end. We're in submission shape.

## Tasks for next week
- [ ] Final report polish (figures, captions, references).
- [ ] Rehearse the 5-minute presentation.
