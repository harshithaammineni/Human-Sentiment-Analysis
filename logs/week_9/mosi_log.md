# Weekly Training Log

**Name:** Mosi Curran
**Student ID:** 6946833
**Week:** Week 9 (13-04-2026 to 19-04-2026)

---

## Tasks completed
- [x] Built the full fusion table in Notebook 06 from Harshitha's `face_resnet18_predictions.csv` and Ravi Teja's `full_image_resnet50_predictions.csv` — one row per image with `face_probs`, `image_probs`, `face_detected_flag`, `num_faces_norm`.
- [x] Trained the fusion MLP (input dim 8, hidden 32, output 3) and shipped `outputs/metrics/fusion_mlp_metrics.json` + the confusion matrix.
- [x] Started the full CLIP Stage 1 run (frozen encoders, 5 epochs) — running overnight; results recorded next week.
- [x] Wrote the Discussion cell of Notebook 06 with per-class numbers and the cross-model comparison table.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `3e4f5a6` | `fusion` | fusion: build feature table from face + image preds | notebooks/06_fusion_model.ipynb, src/fusion.py |
| `7b8c9d0` | `fusion` | fusion: train fusion MLP, save metrics + confusion matrix | notebooks/06_fusion_model.ipynb |
| `e1f2a3c` | `main` | logs(week_9): mosi - fusion shipped, CLIP run kicked off | logs/week_9/mosi_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Fusion MLP | NB 06 | input=8, hidden=32, ep=20, lr=3e-3, bs=128, AdamW, class-weighted CE | **acc 0.389 / macro-F1 0.357 / weighted-F1 0.366** on 4,431 test images |

## Hyperparameters tested
- learning rate: 1e-3 (under-fit at 20 epochs), **3e-3 chosen**, 1e-2 (unstable)
- batch size: 128 (the model is tiny, larger batches help generalisation here)
- epochs: 20 (val loss flat from ~ep 12)
- other: hidden dim swept over {16, 32, 64}; 32 best on val (64 over-fits, 16 under-fits the negative class)

## Results / metrics
- accuracy: **0.389**
- macro F1: **0.357**
- weighted F1: **0.366**
- per-class F1: negative **0.430** (best of all unimodal models), neutral 0.447, positive 0.192
- notes: the MLP trains in ~30 s on CPU. The negative-class lift is the headline takeaway; the positive-class regression is honest and reported.

## Problems found
- Raw `num_faces` (0..7 in the data) was dominating the loss — the MLP just learned a "lots of faces → negative" heuristic.
- Fusion underperformed on positive (F1 0.192) — worse than either single branch (0.323 face, 0.250 image).

## Fixes made
- Normalised to `num_faces_norm = num_faces / max(num_faces)` so the feature contributes a 0..1 signal, not a magnitude.
- Documented the positive-class regression honestly in the Discussion cell rather than masking it — fusion is a re-weighting, not a magic boost, and the report should say so.

## Observations / insights
- The fusion MLP is genuinely useful for the *negative* class (where multi-face dialogue scenes correlate with negative sentiment in MSCTD) but it does not rescue the *positive* class — that's what the multimodal CLIP model is for.
- Fusion sits in the same ~0.36-0.38 macro-F1 band as the unimodal models. Honest comparison rather than an inflated hero number.

## Tasks for next week
- [ ] Finish the CLIP Stage 1 run, ship metrics + confusion matrix + training curve.
- [ ] Update `final_model_comparison.csv` with the CLIP row and regenerate the bar chart.
