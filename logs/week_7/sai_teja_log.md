# Weekly Training Log

**Name:** Tharigopula Sai Teja
**Student ID:** 6945944
**Week:** Week 7 (30-03-2026 to 05-04-2026)

---

## Tasks completed
- [x] Read up on Part 2 (frequency / spatial / brightness degradations) and surveyed `torchvision.transforms.v2`, `albumentations` and `kornia` for the augmentation families we'll need.
- [x] Drafted `src/transforms.py::make_degradation` with three named families: `frequency` (Gaussian blur + additive Gaussian noise), `spatial` (random affine + cutout) and `brightness` (gamma + colour jitter).
- [x] Wrote `mixed_train_transform(face_size, p_degrade=0.5)` for Experiment C in Notebook 04, before the face crops physically exist.
- [x] Reviewed Sameer's stratified split so I know that test-time class drift will not be a confounder when I report robustness deltas later.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `6b7c8d9` | `aug-robust` | aug: degradation families (frequency / spatial / brightness) | src/transforms.py |
| `e0f1a2b` | `aug-robust` | aug: mixed train transform with p_degrade switch | src/transforms.py |
| `3c4d5e6` | `main` | logs(week_7): sai-teja - augmentation toolkit drafted | logs/week_7/sai_teja_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Visualisation of each degradation family on 8 sample faces | scratch notebook | sigma_blur=2, noise_std=0.05, gamma in [0.5,1.5] | qualitative — all three families visibly destroy facial cues without erasing the face |

## Hyperparameters tested
- learning rate: n/a (no training yet)
- batch size: n/a
- epochs: n/a
- other: degradation strengths chosen so that a human can still classify the sentiment from the face — this is the project spec's intent (robustness, not adversarial).

## Results / metrics
- accuracy: n/a
- macro F1: n/a
- weighted F1: n/a
- notes: I'll need ~28k face crops from Harshitha before I can run Experiment B/C — coordinated with her to use the same `data/faces/` layout.

## Problems found
- `albumentations` adds a non-trivial install footprint and a second image format (numpy vs PIL) — extra friction with `torchvision`.
- The `transforms.v2` Gaussian blur is sigma-parameterised slightly differently between PyTorch versions.

## Fixes made
- Dropped `albumentations`; everything in `make_degradation` is `torchvision.transforms.v2` so we keep one codepath end-to-end.
- Pinned `torchvision>=0.17` in `requirements.txt` and pre-instantiated each blur kernel size to skip the per-call sigma normalisation.

## Observations / insights
- The "frequency" family is going to be the most punishing on facial expression recognition because expression cues live in mid-to-high spatial frequencies — this matches what the lab notes on CNN feature maps suggested.
- I want the degraded test set materialised on disk so Harshitha and I can both look at the same images when we compare A vs B.

## Tasks for next week
- [ ] Materialise the degraded test set under `data/degraded_faces/` and ship `outputs/plots/augmentation_examples.png`.
- [ ] Wait on Harshitha's face model before kicking off Experiments A / B / C.
