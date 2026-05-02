# Oral Exam (Viva) Preparation -- EEEM068 Human Sentiment Analysis

The Q&A is **15 minutes per group**, and questions are directed at *individual*
students. Every member must be able to answer questions about every part
of the project. This document is the master answer bank.

> Rule of thumb: keep answers under 60 seconds. Lead with the *what*,
> then *why*, then *trade-off*. If asked a follow-up, expand only on the
> point queried.

---

## A. Dataset & problem framing

**Q1. Why did you use only the En-De portion of MSCTD?**
- The brief mandates it. MSCTD provides parallel En-De and En-Zh splits;
  using only En-De keeps the language model side consistent and matches
  the spec.

**Q2. How did you split the data?**
- Pooled the official train/dev/test, re-stratified into 70/15/15 on
  `label_id` with `sklearn.model_selection.train_test_split`,
  random_state=42 (`src/dataset.py::stratified_split`).
- Re-stratified because MSCTD's official dev/test are small and we
  needed enough validation samples for early stopping.

**Q3. Was the dataset balanced?**
- Mildly imbalanced: `neutral` is the majority class. We address this with
  (a) macro-F1 as the headline metric and (b) inverse-frequency class
  weights in `nn.CrossEntropyLoss`.

**Q4. Why macro-F1 and not accuracy?**
- Accuracy rewards predicting the majority class. Macro-F1 averages F1
  per class equally, exposing failures on the minority class.

**Q5. What makes image-based sentiment hard?**
- Visual sentiment cues are sparse and ambiguous; one frame can be
  read as neutral or mildly positive depending on context (Section
  III-A discussion).

---

## B. Face model (Part 1)

**Q1. Why MTCNN?**
- It cascades three lightweight CNNs (P-Net, R-Net, O-Net), is fast on
  GPU, ships in `facenet-pytorch`, and produces aligned crops out of
  the box.

**Q2. How did you handle multiple faces?**
- Each face is saved as a separate row in `face_metadata.csv`. The face
  model is trained per face. At inference time, we average the per-face
  softmax probabilities to a single image-level vector
  (`src/fusion.py::aggregate_face_predictions`). This is **late label
  fusion**, motivated in Section III-B.

**Q3. What about images with no detected face?**
- `num_faces = 0`, `face_detected_flag = 0`. For fusion we replace the
  missing face probabilities with the *training-prior* over labels so
  the network gets a sane numerical input; the `face_detected_flag`
  lets it learn to ignore that part of the vector.

**Q4. Why ResNet-18 and not ResNet-50 for faces?**
- The face crops are small (224 px) and the dataset is moderate. R-18
  has fewer parameters (~11M) and trains faster while reaching similar
  accuracy on faces; we use R-50 only for the full-image stage where
  scene complexity rewards more capacity.

**Q5. Why might face-only sentiment classification fail?**
- (i) Many MSCTD images contain no face; (ii) some faces are partially
  occluded or in profile; (iii) micro-expressions for `neutral` are
  subtle. Fusion with full-image features addresses these.

---

## C. Robustness & augmentation (Part 2)

**Q1. Why brightness, spatial and frequency families?**
- Direct quote from the brief. Each targets a different failure mode:
  brightness/contrast covers lighting changes, spatial covers pose and
  framing, frequency covers blur/noise/compression.

**Q2. Which degradation reduced performance the most?**
- Frequency typically wins (blur + JPEG re-compression remove
  high-frequency cues that micro-expressions rely on). Confirm with
  the numbers in `outputs/metrics/robustness_results.csv`.

**Q3. Did augmentation improve generalisation?**
- Yes: experiment C (mixed training) recovers most of the macro-F1 lost
  on the degraded test set while staying competitive on original images.

**Q4. Why mix degraded + original at training rather than train only on
  degraded?**
- Distribution shift: the test set still contains original images, so
  mixing keeps the model's representation balanced.

---

## D. Full-image transfer learning (Part 3)

**Q1. Why did you freeze the backbone?**
- The brief explicitly requires it. Practically, with a frozen backbone
  we only train ~1M parameters in the MLP head, which is fast, less
  prone to over-fitting on a moderate-size dataset, and reuses the
  rich ImageNet representation.

**Q2. Why ResNet-50 specifically?**
- Strong ImageNet baseline, ~25M params, well-supported in torchvision,
  feature dim 2048 fits comfortably into our 512/128/3 MLP. ViT-B/16
  is a drop-in alternative (`build_full_image_model("vit_b_16")`).

**Q3. What can the full image capture that faces cannot?**
- Scene context, body posture, props, lighting, social configuration,
  camera angle. Crucial for `neutral` and for no-face images.

**Q4. Why not fine-tune the backbone?**
- Risk of catastrophic forgetting on a small dataset and -- again --
  the project constraint forbids it.

---

## E. Fusion (Part 4)

**Q1. Why does fusion help?**
- Different sources fail in different cases. Late fusion lets the model
  *learn* a per-image weighting between the two streams using
  `face_detected_flag` and `num_faces_norm`.

**Q2. Why late fusion instead of feature-level (early) fusion?**
- Late fusion is robust to missing modalities (no face -> we still have
  image probs) and is much cheaper to train -- the fusion MLP has only
  ~600 parameters.

**Q3. How is `num_faces_norm` defined?**
- Number of detected faces, capped at 5 (`NUM_FACES_CAP` in
  `src/fusion.py`), divided by 5. This keeps the value in [0,1] and
  prevents one outlier crowd scene from dominating.

**Q4. What happens when no face is detected?**
- `face_detected_flag = 0`; face probabilities are replaced with the
  training-set label prior. The MLP learns to rely more on image probs
  in that case.

---

## F. Multimodal CLIP (Extra credit)

**Q1. Why CLIP?**
- Already aligns image and text in a shared 512-dim space via 400M-pair
  contrastive pretraining. Concatenating its image and text projections
  gives a strong multimodal embedding before any fine-tuning.

**Q2. How did you combine the two modalities?**
- Concatenate image and text projection vectors -> small MLP head.
  This is *late* fusion of vector embeddings, the simplest stable
  approach. Cross-attention (LXMERT/ClipBERT) was rejected because of
  instability on small datasets.

**Q3. Was CLIP fine-tuned or frozen?**
- Default: frozen. We only train the MLP. There is an optional Stage 2
  that unfreezes the last transformer block of each tower at LR
  1e-5 -- we report it only if it improves results.

**Q4. Does multimodal help?**
- Where text is informative (clear emotional language), multimodal
  matches or beats fusion. On MSCTD many utterances are short and
  generic, so the gain is moderate -- which we discuss in Section IV-D.

---

## G. Code, reproducibility, contribution

**Q1. How is your code structured?**
- `src/` for importable modules (`config`, `dataset`, `face_detection`,
  `transforms`, `models`, `train`, `evaluate`, `fusion`, `utils`),
  `notebooks/` for orchestration. All paths and hyperparameters live
  in `src/config.py`.

**Q2. How can someone reproduce your results?**
- `pip install -r requirements.txt`, place MSCTD En-De under `data/raw/`,
  run notebooks 01..07 in order. Every notebook calls
  `seed_everything(42)`. See `run_instructions.md`.

**Q3. Where are logs and metrics saved?**
- Per-model JSON in `outputs/metrics/`, predictions in
  `outputs/predictions/`, CMs in `outputs/confusion_matrices/`,
  the comparison table in `outputs/tables/final_model_comparison.csv`,
  weekly individual logs in `logs/week_<n>/<name>_log.md`.

**Q4. How did you ensure every member contributed?**
- Weekly markdown logs per member, tagged commits, branch-per-feature
  workflow, weekly TA check-ins. The `logs/` folder is the audit trail.

---

## H. Mock individual questions (for practice)

Pick one card per round, take 30 seconds to think, answer in <=60 seconds.

1. Walk me through what happens when an image with no face hits your
   fusion model.
2. If I doubled the brightness severity, which model would degrade
   most? Why?
3. Why is `nn.BCEWithLogitsLoss` not what we use here?
4. What would change if MSCTD had 10 sentiment classes instead of 3?
5. Show me where in the code the backbone is frozen, and how you
   verified it actually is.
6. Why do you save predictions to CSV instead of recomputing them in
   the fusion notebook?
7. The validation loss starts increasing at epoch 8 -- what does our
   training loop do?
8. Why might the augmented model perform *worse* than the baseline on
   the original test set?
9. What's the difference between `weighted_f1` and `macro_f1`, and
   when would they disagree?
10. If we wanted to deploy this model, what's the slowest part of the
    pipeline and how would you speed it up?
