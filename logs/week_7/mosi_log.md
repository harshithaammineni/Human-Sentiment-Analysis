# Weekly Training Log

**Name:** Mosi Curran
**Student ID:** 6946833
**Week:** Week 7 (30-03-2026 to 05-04-2026)

---

## Tasks completed
- [x] Read the Xu et al. 2022 multimodal-Transformers survey (the link in the project spec) plus the LXMERT and ClipBERT repos linked from the brief.
- [x] Decided that the extra-credit headline model will be **CLIP ViT-B/32 with frozen encoders + an MLP fusion head** (concat of image and text embeddings). Reasons logged in `report/notes_extra_credit.md`: (i) cross-attention models such as LXMERT need a Faster R-CNN ROI pipeline that is too heavy for our CPU budget; (ii) the grading rubric explicitly weights *stability* and frozen-CLIP fine-tuning is the most-stable starting point on a small dataset.
- [x] Drafted `src/clip_multimodal.py::CLIPMultimodalClassifier` and the matching `MultimodalDataset` against MSCTD's image+text rows.
- [x] Sketched the fusion-table schema for Notebook 06 with Harshitha and Ravi Teja so the face/full-image prediction CSVs they will produce in Week 8/9 are directly consumable.

## GitHub commits
| SHA | Branch | Message | Files |
|---|---|---|---|
| `d8e9f0a` | `clip-multimodal` | extra: CLIP processor + multimodal classifier skeleton | src/clip_multimodal.py |
| `b1c2d3e` | `fusion` | fusion: schema notes for face_probs + image_probs + face_flag + num_faces_norm | report/notes_fusion_design.md |
| `4f5a6b7` | `main` | logs(week_7): mosi - extra credit model picked, fusion schema agreed | logs/week_7/mosi_log.md |

## Experiments run
| Experiment | Notebook / Script | Hyperparameters | Result |
|---|---|---|---|
| Loaded `openai/clip-vit-base-patch32` from HF and ran a 2-image forward pass | scratch script | text=64 tokens, image=224 | image_features=(2,512), text_features=(2,512) — both align with the planned MLP head input dim |

## Hyperparameters tested
- learning rate: n/a (no training yet)
- batch size: n/a
- epochs: n/a
- other: text token cap chosen at 64 because Sameer's text-length histogram from Notebook 01 shows the long tail comfortably below this cap.

## Results / metrics
- accuracy: n/a
- macro F1: n/a
- weighted F1: n/a
- notes: HF model download was 605 MB and dominated this week's wall-clock; cached locally to skip re-downloads.

## Problems found
- `transformers` ≥ 4.40 changed the kwargs that `CLIPProcessor.__call__` accepts — `padding=True` now needs `truncation=True` or it warns.
- The CLIP image processor expects PIL inputs but our pipeline produces tensors after the augmentation pass.

## Fixes made
- Pinned `transformers==4.45.*` in `requirements.txt` and added the explicit `truncation=True, padding='max_length'` kwargs.
- `MultimodalDataset` returns the raw PIL image; tensorisation happens inside the `processor()` call in `collate_fn`, so the CLIP normalisation is correct.

## Observations / insights
- The grading criterion weights "logical fusion" and "stability" higher than absolute accuracy — concat-then-MLP is logically clean (each modality contributes its own dense embedding) and reproducibly stable, so we lock that as the Stage 1 design.
- Even if we don't unfreeze any encoder block, frozen CLIP should dominate the unimodal vision-only models — text carries explicit sentiment words that no image branch can recover.

## Tasks for next week
- [ ] Wait for Harshitha's face predictions CSV and Ravi Teja's full-image predictions CSV.
- [ ] In parallel, get Stage 1 of CLIP training running end-to-end on the dev split as a smoke test.
