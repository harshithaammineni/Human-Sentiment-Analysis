# Weekly Training Log

**Name:** Kakumanu Ravi Teja
**Student ID:** 6905377
**Week:** Week 7 (30-03-2026 to 05-04-2026)

---

## Tasks completed
- [x] Compared candidate full-image backbones (ResNet50, ViT-B/16, Swin-T) against the Part 3 *frozen-backbone* constraint and the CPU budget; picked `resnet50` for the headline run because it gives the best accuracy/latency trade and ImageNet-pretrained weights are reliably available via `torchvision`.
- [x] Wrote `src/models.py::build_full_image_model(backbone='resnet50')` with `param.requires_grad = False` on every backbone tensor and an MLP head (2048 → 512 → 256 → 3) on top.
- [x] Drafted `src/transforms.py::standard_train_transform / standard_eval_transform` for full-image inputs (resize 256, centre-crop 224, ImageNet mean/std).
- [x] Confirmed with Sameer that the master CSV exposes `image_path` for the full image, not the face crop, so `FullImageDataset` can be wired straight to it.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `7f8a9b0` | `full-image` | model: build_full_image_model with frozen backbone + MLP head | src/models.py |
| `c1d2e3f` | `full-image` | model: standard full-image transforms (224 crop, ImageNet norm) | src/transforms.py |
| `4a5b6c7` | `main` | logs(week_7): ravi-teja - full-image backbone selected, head designed | logs/week_7/ravi_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Frozen-backbone parameter audit | scratch script | resnet50, only MLP head trainable | 23.5M frozen params, 1.18M trainable params (head only) |
| Forward-pass smoke test | scratch script | bs=4, 224×224 | output shape (4,3) — head wiring correct |

## Hyperparameters tested
- learning rate: n/a (no training yet)
- batch size: n/a
- epochs: n/a
- other: head shape — tested 2048→128 (too lossy on val pilot) vs 2048→512→256 (chosen).

## Results / metrics
- accuracy: n/a
- macro F1: n/a
- weighted F1: n/a
- notes: head-only forward pass is ~75 ms per batch of 32 on this CPU, so a full epoch on 21k images is projected at ~30 min. Fits the local-CPU constraint.

## Problems found
- `torchvision` deprecated `pretrained=True` in favour of `weights=ResNet50_Weights.IMAGENET1K_V2`; older Colab kernels still error.
- Frozen-backbone forward + autograd was wasting time tracking gradients I didn't want.

## Fixes made
- Wrapped the weight loader in a try/except that falls back to the legacy API if `weights=` fails — keeps Colab compatibility for whoever wants to redo the run there.
- Wrapped the backbone forward in `torch.no_grad()` inside `forward()` so the head trains without computing gradients through the frozen ResNet (≈30% wall-clock saving).

## Observations / insights
- The Part 3 constraint ("backbone must remain frozen") makes ResNet50 the safer choice over ViT-B/16: a frozen ViT head needs more capacity above it because the [CLS] token is too narrow without fine-tuning, and we don't have that compute.
- The same `FullImageDataset` will be reused for the fusion model's image branch — Mosi only needs the predictions CSV from me.

## Tasks for next week
- [ ] Train the frozen-backbone full-image model in Notebook 05 and ship `outputs/predictions/full_image_resnet50_predictions.csv` for Mosi.
- [ ] Run a quick `vit_b_16` ablation if time permits, to put a number on the backbone-choice claim above.
