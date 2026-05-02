# Weekly Training Log

**Name:** Mosi Curran
**Student ID:** 6946833
**Week:** Week 10 (20-04-2026 to 26-04-2026)

---

## Tasks completed
- [x] Finished the CLIP Stage 1 training (frozen encoders, 5 epochs) and shipped `outputs/metrics/clip_multimodal_metrics.json`, the confusion matrix, and the training curve.
- [x] Updated `outputs/tables/final_model_comparison.csv` with the CLIP row and regenerated the bar chart (`outputs/plots/final_comparison_bar.png`).
- [x] Wrote the Methodology Part 4 (Fusion Model) + Extra Credit (Multimodal CLIP) sections of the report and the matching Discussion cells in Notebook 06 and Notebook 07.
- [x] Coordinated the final model-comparison story for the presentation — fusion lifts the negative class, CLIP delivers the headline result.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `7b8c9d1` | `clip-multimodal` | extra: ship final CLIP Stage 1 metrics + training curve | notebooks/07_multimodal_extra_credit.ipynb, outputs/metrics/clip_multimodal_metrics.json |
| `2e3f4a6` | `fusion` | fusion: refresh final_model_comparison.csv + bar chart with CLIP row | notebooks/06_fusion_model.ipynb, outputs/tables/final_model_comparison.csv, outputs/plots/final_comparison_bar.png |
| `5d6e7f8` | `report` | report: methodology + extra credit sections (fusion + CLIP) | report/sections/03_methodology.tex, report/sections/04_results.tex, report/sections/05_extra_credit.tex |
| `9a0b1c3` | `main` | logs(week_10): mosi - CLIP final, comparison + report sections | logs/week_10/mosi_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| CLIP multimodal Stage 1 (final) | NB 07 | bs=32, lr=5e-4, ep=5, frozen encoders, AdamW, weight_decay=1e-2 | **acc 0.570 / macro-F1 0.562 / weighted-F1 0.567** on 4,431 test images |
| Stage 2 toggle (last block unfrozen, lr=1e-5) | NB 07 (`do_stage2=True` smoke) | 1 ep, dev set | dev macro-F1 dipped 0.01 vs Stage 1 — left `do_stage2=False` as default per stability criterion |

## Hyperparameters tested
- learning rate: 1e-3 (early-stopped, unstable on val), **5e-4 chosen**, 1e-4 (under-fit at 5 epochs)
- batch size: 32 (CPU memory cap)
- epochs: 5 (val loss flat from ep 4)
- other: text token cap = 64; image size = 224. Class-weighted CE retained for parity with the unimodal models.

## Results / metrics
- accuracy: **0.570**
- macro F1: **0.562**
- weighted F1: **0.567**
- per-class F1: negative **0.535**, neutral **0.629**, positive **0.522** — every class clears 0.5 for the first time in the project
- notes: training run took ~92 min on local CPU. No NaN, no class collapse, exactly the stability profile the grading rubric weights highly.

## Problems found
- Initial 1e-3 run had a single batch with a NaN loss on epoch 3 (Ravi Teja caught it via the loss-monitoring hook); root cause was an empty caption sneaking through the train-side collator.
- The "headline number" for the project is now 0.562 macro-F1 — needs honest framing against the 0.378 unimodal best, not as a "fusion magic" story.

## Fixes made
- Pulled Ravi Teja's `_safe_text(t)` extension into the train collator; rerun produced zero NaN.
- Wrote the Discussion cells (NB 06 and NB 07) and the report's Section IV-D to be explicit: the +0.18 macro-F1 lift is the *text modality*, not a clever architecture trick.

## Observations / insights
- Concat-fusion of frozen CLIP image+text embeddings, with a tiny MLP on top, is the right design for this dataset and this hardware. It's stable, reproducible, and dominates the unimodal pipeline.
- The fact that *every* class clears 0.5 F1 for the first time (positive class jumped from 0.323 face / 0.250 image / 0.192 fusion → 0.522 CLIP) is the single most informative result in the project — the text channel carries the explicit-sentiment-word signal that no purely visual model can recover.

## Tasks for next week
- [ ] Final presentation slides for Parts 4 + Extra Credit.
- [ ] Be ready to defend the concat-fusion choice over cross-attention in the viva.
