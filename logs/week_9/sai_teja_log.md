# Weekly Training Log

**Name:** Tharigopula Sai Teja
**Student ID:** 6945944
**Week:** Week 9 (13-04-2026 to 19-04-2026)

---

## Tasks completed
- [x] Notebook 04 Experiment A / B / C end-to-end: ran A (Harshitha's clean checkpoint on clean test), B (clean checkpoint on degraded test), and C (aug-trained checkpoint on both).
- [x] Trained the aug-trained face ResNet18 from scratch using `mixed_train_transform(p_degrade=0.5)`.
- [x] Shipped `outputs/metrics/robustness_results.csv` and the four matching confusion matrices.
- [x] Wrote the Discussion cell of Notebook 04 with the observed numbers.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `9c0d1e2` | `aug-robust` | aug: train face model with mixed degraded transform (Exp C) | notebooks/04_augmentation_robustness.ipynb, src/train.py |
| `3a4b5c6` | `aug-robust` | aug: ship robustness_results.csv (A/B/C × 2 evals) | outputs/metrics/robustness_results.csv |
| `7d8e9f0` | `main` | logs(week_9): sai-teja - robustness experiment complete | logs/week_9/sai_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| A: orig-trained → orig test | NB 04 | same as Week 8 face training | acc **0.382** / macro-F1 **0.378** |
| B: orig-trained → degraded test | NB 04 | eval-only, degraded test | acc **0.357** / macro-F1 **0.322** |
| C-train: aug-trained from scratch | NB 04 | bs=64, lr=3e-4, ep=10, p_degrade=0.5, class-weighted CE | trains stably, val macro-F1 0.36-0.37 from ep 5 onward |
| C-eval orig: aug-trained → orig test | NB 04 | eval-only | acc **0.368** / macro-F1 **0.366** |
| C-eval deg: aug-trained → degraded test | NB 04 | eval-only | acc **0.366** / macro-F1 **0.361** |

## Hyperparameters tested
- learning rate: 3e-4 (matched Harshitha's Week 8 setting; deliberately not retuned so the only change between A and C is the augmentation)
- batch size: 64
- epochs: 10
- other: `p_degrade` swept over {0.25, 0.5, 0.75}; 0.5 chosen — 0.25 didn't close the robustness gap, 0.75 lost ~0.02 macro-F1 on clean.

## Results / metrics
- accuracy: 0.382 / 0.357 / 0.368 / 0.366 (A / B / C-orig / C-deg)
- macro F1: **0.378 / 0.322 / 0.366 / 0.361**
- weighted F1: 0.379 / 0.321 / 0.365 / 0.362
- notes: the **5.5-point** A→B drop shrinks to a **0.5-point** C-orig vs C-deg gap — augmentation closes the robustness gap by ~10×.

## Problems found
- Naive per-family recall on Exp B suggested the model was *miscalibrated* toward negative under degradation — looked like a bug at first.
- Aug-trained model's val loss curve was noisier than the clean-trained model's, even with the deterministic `(image_id, epoch)` seeding from Week 8.

## Fixes made
- Confirmed (with Harshitha) that the degradation is class-agnostic; the negative-collapse is a genuine model behaviour, not a data leak.
- Added a 1-epoch warm-up at p_degrade=0 then ramped to 0.5 over epochs 1-3 — smoothed the val curve without changing the final numbers.

## Observations / insights
- Augmentation costs ~1.2 macro-F1 points on clean data (0.378 → 0.366) but buys back ~3.9 macro-F1 points on degraded data (0.322 → 0.361). For any real deployment that's a clear win.
- Frequency-style degradations were the most punishing in the per-family ablation, consistent with expression cues living at mid-to-high spatial frequencies.

## Tasks for next week
- [ ] Help write the Experiments section of the report (Part 2).
- [ ] Optional: per-family ablation table for the appendix (frequency vs spatial vs brightness in isolation).
