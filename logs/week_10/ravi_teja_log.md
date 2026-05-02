# Weekly Training Log

**Name:** Kakumanu Ravi Teja
**Student ID:** 6905377
**Week:** Week 10 (20-04-2026 to 26-04-2026)

---

## Tasks completed
- [x] Sanity-checked Mosi's fusion model uses the same image_id keys as my full-image predictions — confirmed (0 missing rows out of 4,431).
- [x] Wrote the Methodology Part 3 (Full-Image Transfer Learning) and Experiments Part 3 sections of the report, including the ViT-B/16 ablation table from Week 9.
- [x] Polished Notebook 05's Discussion cell with the per-class numbers (neutral 0.492, negative 0.345, positive 0.250) and the explicit "complementarity with the face branch" framing.
- [x] Helped Mosi debug a 200-line outlier in the CLIP training where one batch produced a NaN in the loss (turned out to be an empty caption that slipped past the Week 8 substitute fix).

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `6f7a8b9` | `report` | report: methodology + experiments Part 3 (full-image transfer learning) | report/sections/03_methodology.tex, report/sections/04_results.tex |
| `0c1d2e4` | `clip-multimodal` | extra: harden empty-caption substitution in CLIP dataset | src/clip_multimodal.py |
| `3e4f5a7` | `main` | logs(week_10): ravi-teja - report Part 3 + CLIP NaN fix | logs/week_10/ravi_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Full-image image_id key audit | scratch script | merge full_image_resnet50_predictions.csv ↔ master | 4,431 / 4,431 rows matched, no NaN |

## Hyperparameters tested
- learning rate: n/a
- batch size: n/a
- epochs: n/a
- other: n/a

## Results / metrics
- accuracy: 0.391 (full-image — final, unchanged from Week 8/9)
- macro F1: 0.362
- weighted F1: 0.373
- notes: ViT-B/16 ablation kept in the appendix as Table A.1; macro-F1 0.349 vs ResNet50's 0.362 — close enough that I frame the choice in terms of CPU budget.

## Problems found
- Mosi's CLIP training emitted a NaN at batch 47 of epoch 3 — caught by his loss-monitoring hook.
- The full-image confusion matrix figure was being saved at 96 dpi, which looked fuzzy in the IEEE PDF.

## Fixes made
- The empty-caption substitute fix from Week 8 was only being applied to *test*-loaded rows; extended the same `_safe_text(t)` helper to the train collator. NaN gone on re-run.
- Re-saved every confusion matrix at 180 dpi via `plt.savefig(..., dpi=180, bbox_inches='tight')`.

## Observations / insights
- The full-image branch's "scene context wins on neutral, loses on positive" pattern is the cleanest cross-class story in the project. It motivates both the fusion model (which exploits the complementarity) and the CLIP model (which fixes the positive-class weakness via text).
- Catching the CLIP NaN early was the kind of pair-debugging that made the difference between "stage 1 trains stably" and "stage 1 emits a single corrupt run". Worth flagging in the viva.

## Tasks for next week
- [ ] Slide deck for Part 3 (frozen-backbone justification, per-class breakdown).
- [ ] Be ready to defend the ResNet50 vs ViT choice in the viva.
