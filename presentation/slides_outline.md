# Group Presentation Outline (5 slides, 5 minutes)

Use this as the storyboard for `slides.pptx`. One speaker per slide; aim
for ~60 seconds each. The 15-minute Q&A follows.

---

## Slide 1 -- Problem & Dataset
**Speaker: Shaik Sameer**

- Task: 3-class sentiment (negative / neutral / positive) on MSCTD En-De.
- Why hard: visual sentiment cues are sparse, ambiguous, context-dependent.
- Data: pooled MSCTD En-De, re-stratified into 70/15/15.
- Visual: class distribution bar chart (`class_distribution.png`).

## Slide 2 -- Face Pipeline & Robustness
**Speaker: Ammineni Harshitha**

- MTCNN (`facenet-pytorch`) -> 224x224 face crops.
- ResNet-18 face classifier; multi-face handled by mean of softmax;
  no-face handled by `face_detected_flag` + label prior.
- Three degradation families (frequency / spatial / brightness);
  augmented training closes most of the robustness gap.
- Visual: augmentation grid (`augmentation_examples.png`) + robustness
  table.

## Slide 3 -- Full-Image & Fusion Models
**Speaker: Kakumanu Ravi Teja**

- Frozen ResNet-50 backbone + custom MLP (Part 3).
- Late-fusion MLP that ingests `[face_probs, image_probs, num_faces, flag]`.
- Fusion is small (~600 params) but learns when to trust each stream.
- Visual: pipeline diagram (in README) + fusion CM.

## Slide 4 -- Results
**Speaker: Tharigopula Sai Teja**

- Final comparison table from `final_model_comparison.csv`.
- Bar chart of macro-F1 across all models.
- Headline finding: fusion > face-only; CLIP multimodal competitive.
- Visual: `final_comparison_bar.png`.

## Slide 5 -- Conclusion, Future Work, Extra Credit
**Speaker: Mosi Curran**

- Key takeaways: complementarity of face/scene cues; augmentation
  improves robustness; CLIP gives multimodal lift.
- Limitations: dataset size, dialogue text often short.
- Future: cross-attention fusion, video extension, sentiment-aware
  tokenisation.
- Visual: 1-line summary of CLIP results.

---

## Speaker tips
- Practise transitions: each speaker introduces the next slide's owner.
- Have one *backup slide* per speaker in the appendix in case of Q&A.
- Bring a printed copy of `viva_questions.md` to the viva.
