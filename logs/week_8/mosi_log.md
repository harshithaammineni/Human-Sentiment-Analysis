# Weekly Training Log

**Name:** Mosi Curran
**Student ID:** 6946833
**Week:** Week 8 (06-04-2026 to 12-04-2026)

---

## Tasks completed
- [x] Smoke-tested the CLIP Stage 1 training loop end-to-end on the 4,572-image dev split — 1 epoch at lr=1e-3 against the frozen encoders runs in ~22 min on CPU and produces a healthy decreasing loss.
- [x] Locked the fusion feature schema with Harshitha (face_probs ∈ R^3) and Ravi Teja (image_probs ∈ R^3) plus `face_detected_flag` and `num_faces_norm`.
- [x] Wrote `src/fusion.py::aggregate_face_predictions` that collapses multiple per-face predictions to a single per-image vector (mean over face softmaxes + face count).
- [x] Drafted Notebook 06 cells 1-4 (build fusion table, train MLP) but left them unrun until Harshitha's and Ravi Teja's CSVs landed.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `a4b5c6d` | `clip-multimodal` | extra: Stage 1 smoke test on dev split, frozen encoders | notebooks/07_multimodal_extra_credit.ipynb, src/clip_multimodal.py |
| `e7f8a9b` | `fusion` | fusion: aggregate_face_predictions + per-image feature builder | src/fusion.py, notebooks/06_fusion_model.ipynb |
| `c0d1e2f` | `main` | logs(week_8): mosi - CLIP smoke OK, fusion plumbing drafted | logs/week_8/mosi_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| CLIP Stage 1 smoke (1 epoch on dev) | NB 07 | bs=32, lr=1e-3, frozen encoders | loss 1.10 → 0.92 in 1 epoch — pipeline works, no NaN, no class collapse |

## Hyperparameters tested
- learning rate: 1e-3 (smoke test only, will retune for the full run)
- batch size: 32 (CPU memory limits)
- epochs: 1 (smoke)
- other: text token cap = 64, image size = 224 (standard CLIP)

## Results / metrics
- accuracy: n/a (smoke run, not the production training set)
- macro F1: n/a
- weighted F1: n/a
- notes: CLIP image+text forward+backward is ~1.6 s/step at bs=32, so a full train epoch on 21k samples is projected at ~18 min — comfortably runnable next week.

## Problems found
- At `freeze_encoders=True` PyTorch was still allocating gradient buffers for every encoder param.
- The CLIP processor refused to batch when text was empty, which happens for ~0.4% of MSCTD rows where the utterance is blank.

## Fixes made
- `requires_grad=False` everywhere + a top-level `with torch.no_grad():` around the encoder forward in `CLIPMultimodalClassifier.forward()`.
- `MultimodalDataset` substitutes `"."` for empty utterances — the CLIP text encoder still produces a sane embedding and we don't lose the row.

## Observations / insights
- Stable loss curve on the smoke run reassures me that Stage 1 will not need any of the LXMERT/ClipBERT-style stabilisation tricks.
- The fusion table will only need ~21k rows × ~10 columns — trivially small, so we can keep it as a parquet in `outputs/predictions/` for reuse.

## Tasks for next week
- [ ] Build the full fusion table in Notebook 06 once both prediction CSVs are merged into `main`.
- [ ] Train the fusion MLP and ship its metrics — should be done before I start the full CLIP run in Week 10.
