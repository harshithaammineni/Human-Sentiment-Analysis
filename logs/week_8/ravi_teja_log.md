# Weekly Training Log

**Name:** Kakumanu Ravi Teja
**Student ID:** 6905377
**Week:** Week 8 (06-04-2026 to 12-04-2026)

---

## Tasks completed
- [x] Notebook 05: trained the frozen-backbone ResNet50 + MLP head end-to-end on the 21k full-image training split.
- [x] Verified the Part 3 constraint via a parameter-count audit at the top of training: 23.5M frozen / 1.18M trainable.
- [x] Saved metrics + confusion matrix + the per-image predictions CSV (`outputs/predictions/full_image_resnet50_predictions.csv`) for Mosi.
- [x] Helped Sameer trace the seeding bug — the same dataloader was returning slightly different batches between his run and mine before the seeding refactor.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `5c6d7e9` | `full-image` | full-image: train ResNet50 frozen + MLP head end-to-end | notebooks/05_full_image_model.ipynb, src/train.py |
| `8f9a0b1` | `full-image` | full-image: save predictions CSV for fusion | src/eval.py |
| `c2d3e4f` | `main` | logs(week_8): ravi-teja - full-image model trained, predictions shipped | logs/week_8/ravi_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Frozen-ResNet50 + MLP head | NB 05 | bs=64, lr=1e-3, ep=10, AdamW, head dropout=0.3, class-weighted CE | **acc 0.391 / macro-F1 0.362 / weighted-F1 0.373** on 4,431 test images |

## Hyperparameters tested
- learning rate: 3e-4 (slow), 1e-3 (chosen, smooth val curve), 3e-3 (overfit head by ep 4)
- batch size: 64 (chosen)
- epochs: 10 (val loss minimum at ep 8, kept that checkpoint)
- other: head dropout swept over {0.1, 0.3, 0.5}; 0.3 best on val

## Results / metrics
- accuracy: **0.391**
- macro F1: **0.362**
- weighted F1: **0.373**
- per-class F1: neutral 0.492, negative 0.345, positive 0.250
- notes: ~32 min per epoch on local CPU; metrics in `outputs/metrics/full_image_resnet50_metrics.json`.

## Problems found
- The MLP head wanted to overfit fast at lr=3e-3 (val loss climbed after ep 3 even with head dropout 0.5).
- The first run produced a (4431, 4) predictions CSV — I'd accidentally written the logits, not the softmax probabilities, which would have broken Mosi's fusion table.

## Fixes made
- Locked lr=1e-3 + head dropout 0.3 as the production config.
- `evaluate_and_save` now writes softmax probabilities (`pred_proba_neg/neu/pos`) plus argmax — Mosi confirmed this is exactly the schema the fusion model expects.

## Observations / insights
- Full-image dominates on neutral (recall 0.605) where the face branch was weakest — exactly the complementarity the fusion model is built around.
- Positive recall is poor (0.197) because positive scenes are visually heterogeneous and the frozen backbone has no way to specialise for them. Mosi's CLIP model is the obvious counter to this.

## Tasks for next week
- [ ] Hand the predictions CSV to Mosi (done).
- [ ] Optional ablation: re-run with `vit_b_16` frozen if time permits, just to put a number behind the backbone-choice claim from Week 7.
