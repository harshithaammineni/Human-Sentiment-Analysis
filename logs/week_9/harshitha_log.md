# Weekly Training Log

**Name:** Ammineni Harshitha
**Student ID:** 6952560
**Week:** Week 9 (13-04-2026 to 19-04-2026)

---

## Tasks completed
- [x] Re-evaluated the original-trained face ResNet18 on Sai Teja's degraded test set for Experiment B in Notebook 04.
- [x] Co-trained the augmented face ResNet18 with Sai Teja (he ran the training, I supplied the dataset class and the metrics tooling).
- [x] Added per-class precision / recall / F1 to the face metrics JSON so the report's results table can be auto-generated.
- [x] Validated `face_resnet18_predictions.csv` schema against Mosi's `aggregate_face_predictions` consumer — confirmed image_id, face_id, pred_proba_neg/neu/pos columns.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `e8f9a0b` | `face-model` | face: per-class precision/recall in metrics JSON | src/eval.py |
| `1c2d3e4` | `aug-robust` | face: evaluate orig-trained face model on degraded test (Exp B) | notebooks/04_augmentation_robustness.ipynb |
| `5f6a7b8` | `main` | logs(week_9): harshitha - exp B numbers in, schema locked | logs/week_9/harshitha_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Exp B: original-trained face → degraded test | NB 04 cell 7 | same checkpoint as Week 8 | **acc 0.357 / macro-F1 0.322** — a 5.5-point macro-F1 drop vs the clean test |

## Hyperparameters tested
- learning rate: same as Week 8 (Exp B is *evaluation only* of the existing checkpoint)
- batch size: 64 (eval-only)
- epochs: 0 (eval)
- other: kept the seed identical so Sai Teja and I are guaranteed to be on the same per-image indices

## Results / metrics
- accuracy: **0.357** (Exp B)
- macro F1: **0.322** (Exp B)
- weighted F1: **0.321** (Exp B)
- per-class recall on degraded test: negative **0.701** (collapse), neutral 0.178, positive 0.199
- notes: confusion matrix saved to `outputs/confusion_matrices/face_resnet18_test_degraded_cm.png`. The "panic into negative" failure mode is unmistakable.

## Problems found
- The collapse-into-negative behaviour under degradation looked at first like a bug in Sai Teja's `make_degradation` — I worried we were biasing low-light images toward negative.
- Per-class recall metrics were missing from the metrics JSON before this week, so it was hard to *see* the failure mode.

## Fixes made
- Verified the degradation pipeline is class-agnostic by computing the per-family recall on each class separately (each family's recall on negative is uniformly higher than on positive — the bias is the model's, not the augmentation's).
- Added per-class precision/recall to `evaluate_and_save` so every future experiment ships the same table.

## Observations / insights
- The clean → degraded drop on macro-F1 (0.378 → 0.322) is a *real* generalisation gap — not a code bug. The aug-trained model in Sai Teja's Experiment C should close most of it, and that's exactly what the project spec asks us to demonstrate.
- The face branch's positive-class weakness (F1 0.323 clean) plus the degradation-time collapse are both pointing at the same root cause: cropped faces aren't enough.

## Tasks for next week
- [ ] Help Mosi sanity-check the fusion features (face_probs averaging logic on multi-face images).
- [ ] Write the face section of the report's Methodology and Experiments.
