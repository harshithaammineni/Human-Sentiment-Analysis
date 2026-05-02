# Weekly Training Log

**Name:** Ammineni Harshitha
**Student ID:** 6952560
**Week:** Week 10 (20-04-2026 to 26-04-2026)

---

## Tasks completed
- [x] Sanity-checked Mosi's fusion features by spot-checking 30 multi-face images: confirmed `aggregate_face_predictions` is doing a clean mean-of-softmax across the per-face rows and not, e.g., losing the second face.
- [x] Wrote the Methodology Part 1 (Face-Based Analysis) and the Experiments Part 1 paragraph for the report.
- [x] Polished Notebook 02's Discussion cell with the observed face-coverage statistics (3,015 of 4,431 test images yield ≥1 face crop = 68%).
- [x] Built the per-class precision/recall table for the report's Section IV.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `2a3b4c5` | `face-model` | face: per-class precision/recall summary table for report | report/sections/04_results.tex |
| `6d7e8f9` | `report` | report: methodology + experiments Part 1 (face-based) | report/sections/03_methodology.tex, report/sections/04_results.tex |
| `0a1b2c3` | `main` | logs(week_10): harshitha - report sections + fusion sanity check | logs/week_10/harshitha_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Multi-face fusion sanity check | scratch script + NB 06 | 30 sampled images | mean-of-softmax matches manual computation; no row dropped |

## Hyperparameters tested
- learning rate: n/a (no model trained this week)
- batch size: n/a
- epochs: n/a
- other: n/a

## Results / metrics
- accuracy: 0.382 (face model — final, unchanged from Week 8/9)
- macro F1: 0.378
- weighted F1: 0.379
- notes: per-class precision and recall now in the report's results table; confusion matrix figure from `outputs/confusion_matrices/face_resnet18_cm.png` referenced as Fig. 3.

## Problems found
- The first draft of the methodology section over-claimed on the face model — said it "outperforms the prior baseline by 2×" without citing the per-class drop on positive.
- Couple of multi-face images had `face_id=0` repeated (a Week 8 IoU dedup edge case).

## Fixes made
- Rewrote the methodology paragraph to be honest about the positive-class weakness and frame it as the explicit motivation for the fusion + multimodal models.
- Re-ran the IoU dedup with the threshold lifted from 0.85 to 0.80; reduced duplicates to 0 across the test split.

## Observations / insights
- The face branch is doing what it should — a clear, honest, per-class signal. The narrative is "face is necessary but not sufficient" and that is exactly what the rest of the pipeline is designed around.
- Spot-checking fusion features by hand was worth the time: it caught zero bugs, but it gives me confidence to defend the fusion logic in the viva.

## Tasks for next week
- [ ] Rehearse the face-branch portion of the presentation (slides 3-5).
- [ ] Help Mosi write the multimodal section's discussion paragraph.
