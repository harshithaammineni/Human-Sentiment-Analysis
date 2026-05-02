# Weekly Training Log

**Name:** Tharigopula Sai Teja
**Student ID:** 6945944
**Week:** Week 10 (20-04-2026 to 26-04-2026)

---

## Tasks completed
- [x] Wrote the Methodology Part 2 (Data Augmentation) and Experiments Part 2 sections of the report.
- [x] Built the per-family ablation table for the appendix (frequency vs spatial vs brightness applied in isolation to the test set).
- [x] Polished Notebook 04's Discussion cell with the observed numbers and the "panic into negative" failure-mode framing.
- [x] Helped Harshitha by re-running the per-class breakdown for the report's results table.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `4d5e6f7` | `aug-robust` | aug: per-family ablation table for appendix | notebooks/04_augmentation_robustness.ipynb |
| `8a9b0c1` | `report` | report: methodology + experiments Part 2 (augmentation) | report/sections/03_methodology.tex, report/sections/04_results.tex |
| `2c3d4e5` | `main` | logs(week_10): sai-teja - report Part 2 sections | logs/week_10/sai_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Per-family eval — frequency only | NB 04 (appendix cell) | clean checkpoint, frequency degradation only | macro-F1 0.31 (worst) |
| Per-family eval — spatial only | NB 04 (appendix cell) | clean checkpoint, spatial only | macro-F1 0.34 |
| Per-family eval — brightness only | NB 04 (appendix cell) | clean checkpoint, brightness only | macro-F1 0.35 (least harmful) |

## Hyperparameters tested
- learning rate: n/a (eval-only this week)
- batch size: 64
- epochs: 0 (eval)
- other: each family applied at its Week 8 default strength so the numbers are directly comparable.

## Results / metrics
- accuracy: 0.382 / 0.357 / 0.368 / 0.366 (final A / B / C-orig / C-deg from `robustness_results.csv`)
- macro F1: **0.378 / 0.322 / 0.366 / 0.361**
- weighted F1: 0.379 / 0.321 / 0.365 / 0.362
- notes: per-family appendix table corroborates the Notebook 04 Discussion claim that frequency degradations are the most harmful.

## Problems found
- The first version of the per-family appendix table mixed up the row order between frequency and spatial — the numbers were right but the labels were swapped.
- IEEE template was complaining about the per-family table's column width.

## Fixes made
- Rewrote the per-family eval as an explicit `for family in ('frequency', 'spatial', 'brightness')` loop with the family name embedded in the metric file name — no more label confusion.
- Switched the appendix table to `tabularx` with auto-sized columns.

## Observations / insights
- Frequency degradations causing the largest drop matches the lab-3 intuition that mid-frequency components carry expression cues — nice clean story for the report.
- The robustness gap closes by ~10× under augmentation training; this is the headline number for Part 2 and we should plot it as a paired bar chart in the presentation.

## Tasks for next week
- [ ] Add the paired-bar robustness figure to the slides.
- [ ] Be ready to defend the choice of `p_degrade=0.5` in the viva.
