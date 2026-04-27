# Weekly Training Log

**Name:** Kakumanu Ravi Teja
**Student ID:** 6905377
**Week:** Week 9 (13-04-2026 to 19-04-2026)

---

## Tasks completed
- [x] Re-ran the full-image training from a clean seed to confirm the Week 8 numbers reproduce exactly under Sameer's unified `seed_everything(42)`.
- [x] Re-shipped `outputs/predictions/full_image_resnet50_predictions.csv` with the standardised `pred_proba_*` columns Mosi locked in.
- [x] Ran the optional `vit_b_16` ablation: frozen ViT + matched MLP head, same training schedule.
- [x] Wrote the Methodology paragraph for Part 3 of the report (frozen-backbone justification + head architecture).

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `1b2c3d4` | `full-image` | full-image: reproduce Week 8 numbers under unified seeding | notebooks/05_full_image_model.ipynb |
| `5e6f7a8` | `full-image` | full-image: vit_b_16 frozen ablation (appendix) | notebooks/05_full_image_model.ipynb |
| `9b0c1d2` | `main` | logs(week_9): ravi-teja - reproduced + ViT ablation | logs/week_9/ravi_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Full-image ResNet50 + MLP (reproduction) | NB 05 | bs=64, lr=1e-3, ep=10, dropout=0.3 | **acc 0.391 / macro-F1 0.362** — exact match to Week 8 ✓ |
| Full-image ViT-B/16 frozen + MLP (ablation) | NB 05 (appendix cell) | same head, same schedule | acc 0.378 / macro-F1 0.349 — ~1.3 macro-F1 below ResNet50, confirming the Week 7 backbone choice |

## Hyperparameters tested
- learning rate: 1e-3 (production), tested 5e-4 + 2e-3 on the ViT ablation — 1e-3 still best
- batch size: 64
- epochs: 10
- other: head dropout 0.3 retained for both backbones for a clean comparison

## Results / metrics
- accuracy: **0.391** (production) / 0.378 (ViT ablation)
- macro F1: **0.362** (production) / 0.349 (ViT ablation)
- weighted F1: **0.373** (production) / 0.358 (ViT ablation)
- notes: ViT ablation took ~45 min/epoch on CPU vs ~32 min for ResNet50 — even before considering accuracy, ResNet50 is the right call for our hardware budget.

## Problems found
- First reproduction run came back ~0.002 macro-F1 below Week 8 — the gap was the seed bug Sameer fixed mid-week.
- ViT-B/16 forward through `torchvision`'s frozen weights produced a tensor on a different device than the head's parameters when running with `pin_memory=True`.

## Fixes made
- Pulled Sameer's `seed_everything` refactor and re-ran — numbers now match to 4 decimal places.
- Added an explicit `.to(device)` on the backbone output before the head — should never have been needed but it's a one-line guardrail.

## Observations / insights
- The full-image branch's per-class profile (strong on neutral, weak on positive) is the exact mirror image of the face branch's profile (weak on neutral, OK on negative/positive) — strongly suggests fusion will help on at least one class.
- The ViT-B/16 ablation lands within 1.3 macro-F1 of ResNet50 — close enough that we don't claim superiority for one backbone in the report; we just justify the operational choice (CPU budget).

## Tasks for next week
- [ ] Sanity-check Mosi's fusion model on the same held-out indices.
- [ ] Write the full-image (Part 3) section of the report's Methodology.
