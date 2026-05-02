// Build the Week-10 progress presentation for EEEM068 Human Sentiment Analysis.
// Output: progress_presentation.pptx (10 slides, ~10 minutes).
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.author = "EEEM068 Group - Human Sentiment Analysis";
pres.title = "AML Project Progress - Week 10";

// ---------- Palette ----------
const NAVY    = "0B1F3A"; // primary dark
const TEAL    = "1C7293"; // secondary
const MINT    = "5BC0BE"; // accent
const CORAL   = "E07A5F"; // warm accent (in-progress / risk)
const LIGHT   = "F5F7FA"; // light bg
const PAPER   = "FFFFFF";
const INK     = "1A1A2E"; // body text
const MUTED   = "5A6776"; // captions
const RULE    = "D7DBE0";

const FONT_H = "Calibri";
const FONT_B = "Calibri";

// ---------- Helpers ----------
function pageHeader(slide, title, kicker) {
  slide.background = { color: PAPER };
  // top navy strip-free design: just a kicker + title block
  slide.addText(kicker, {
    x: 0.5, y: 0.35, w: 12.3, h: 0.35,
    fontFace: FONT_H, fontSize: 12, bold: true, color: TEAL,
    charSpacing: 6, margin: 0,
  });
  slide.addText(title, {
    x: 0.5, y: 0.7, w: 12.3, h: 0.7,
    fontFace: FONT_H, fontSize: 30, bold: true, color: NAVY, margin: 0,
  });
}

function footer(slide, pageNum, total) {
  slide.addText("EEEM068 Applied Machine Learning  -  University of Surrey  -  Spring 2026", {
    x: 0.5, y: 7.05, w: 9, h: 0.3, fontFace: FONT_B, fontSize: 9, color: MUTED, margin: 0,
  });
  slide.addText(`${pageNum} / ${total}`, {
    x: 12.0, y: 7.05, w: 0.8, h: 0.3, fontFace: FONT_B, fontSize: 9, color: MUTED, align: "right", margin: 0,
  });
}

function pill(slide, x, y, w, h, label, fillColor, textColor) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, fill: { color: fillColor }, line: { color: fillColor, width: 0 }, rectRadius: 0.08,
  });
  slide.addText(label, {
    x, y, w, h, fontFace: FONT_H, fontSize: 10, bold: true, color: textColor,
    align: "center", valign: "middle", margin: 0,
  });
}

const TOTAL_SLIDES = 10;

// =====================================================================
// SLIDE 1 - TITLE
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // accent block
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: MINT }, line: { color: MINT, width: 0 },
  });

  s.addText("PROJECT PROGRESS REPORT  |  WEEK 10", {
    x: 0.9, y: 1.1, w: 11, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: MINT, charSpacing: 8, margin: 0,
  });

  s.addText("Human Sentiment Analysis", {
    x: 0.9, y: 1.55, w: 11.5, h: 0.95,
    fontFace: FONT_H, fontSize: 48, bold: true, color: PAPER, margin: 0,
  });

  s.addText("3-class visual sentiment on the MSCTD En-De multimodal dialogue corpus", {
    x: 0.9, y: 2.55, w: 11.5, h: 0.5,
    fontFace: FONT_H, fontSize: 18, italic: true, color: "C8D6E5", margin: 0,
  });

  // separator line
  s.addShape(pres.shapes.LINE, {
    x: 0.9, y: 3.25, w: 6.0, h: 0,
    line: { color: MINT, width: 2 },
  });

  // group members
  const members = [
    ["Shaik Sameer",          "6944091", "Dataset preparation, GitHub & logs"],
    ["Ammineni Harshitha",    "6952560", "Face extraction & face model"],
    ["Tharigopula Sai Teja",  "6945944", "Augmentation & robustness"],
    ["Kakumanu Ravi Teja",    "6905377", "Full-image transfer learning"],
    ["Mosi Curran",           "6946833", "Fusion model & multimodal CLIP"],
  ];
  let yy = 3.55;
  members.forEach(([name, sid, role]) => {
    s.addText(name, {
      x: 0.9, y: yy, w: 4.4, h: 0.35,
      fontFace: FONT_H, fontSize: 14, bold: true, color: PAPER, margin: 0,
    });
    s.addText(sid, {
      x: 5.3, y: yy, w: 1.6, h: 0.35,
      fontFace: FONT_B, fontSize: 13, color: MINT, margin: 0,
    });
    s.addText(role, {
      x: 7.0, y: yy, w: 5.5, h: 0.35,
      fontFace: FONT_B, fontSize: 12, color: "C8D6E5", italic: true, margin: 0,
    });
    yy += 0.42;
  });

  // bottom meta
  s.addText("Module: EEEM068 Applied Machine Learning   |   Convenor: Dr. Sobhan Asasi   |   Friday, 1 May 2026", {
    x: 0.9, y: 6.95, w: 11.5, h: 0.35,
    fontFace: FONT_B, fontSize: 11, color: "8FA1B5", margin: 0,
  });
}

// =====================================================================
// SLIDE 2 - PROBLEM, DATA, APPROACH
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "Problem, Dataset & Approach", "01  /  CONTEXT");

  // Left column: Task + Why hard
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.65, w: 0.08, h: 4.6, fill: { color: TEAL }, line: { color: TEAL, width: 0 },
  });
  s.addText("Task", {
    x: 0.75, y: 1.6, w: 5.5, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY, margin: 0,
  });
  s.addText([
    { text: "Predict ", options: { fontSize: 13, color: INK } },
    { text: "negative / neutral / positive", options: { fontSize: 13, color: NAVY, bold: true } },
    { text: " sentiment from a single dialogue image (and optionally its English utterance).", options: { fontSize: 13, color: INK } },
  ], { x: 0.75, y: 1.95, w: 5.7, h: 0.9, fontFace: FONT_B, margin: 0 });

  s.addText("Why this is hard", {
    x: 0.75, y: 3.0, w: 5.5, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY, margin: 0,
  });
  s.addText([
    { text: "Sparse, ambiguous facial cues - many neutral/mild expressions", options: { bullet: true, breakLine: true } },
    { text: "No-face frames (objects, side profiles, occlusions) require fallback", options: { bullet: true, breakLine: true } },
    { text: "Multi-speaker scenes need per-face aggregation", options: { bullet: true, breakLine: true } },
    { text: "Class imbalance - macro-F1 is the headline metric", options: { bullet: true } },
  ], {
    x: 0.75, y: 3.4, w: 5.7, h: 2.6,
    fontFace: FONT_B, fontSize: 12, color: INK, paraSpaceAfter: 6, margin: 0,
  });

  // Right column: Dataset card + Approach card
  // Dataset card
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.9, y: 1.55, w: 6.0, h: 2.4,
    fill: { color: LIGHT }, line: { color: RULE, width: 1 }, rectRadius: 0.08,
  });
  s.addText("Dataset - MSCTD (En-De)", {
    x: 7.1, y: 1.65, w: 5.6, h: 0.35,
    fontFace: FONT_H, fontSize: 14, bold: true, color: TEAL, margin: 0,
  });
  s.addText([
    { text: "~30,370 utterances across ~3,000 dialogue scenes", options: { bullet: true, breakLine: true } },
    { text: "Re-stratified 70 / 15 / 15 split at the SCENE level (seed 42) - prevents context leakage", options: { bullet: true, breakLine: true } },
    { text: "Single source of truth: data/processed/msctd_master.csv", options: { bullet: true } },
  ], {
    x: 7.1, y: 2.05, w: 5.7, h: 1.85,
    fontFace: FONT_B, fontSize: 11.5, color: INK, paraSpaceAfter: 4, margin: 0,
  });

  // Approach card
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.9, y: 4.05, w: 6.0, h: 2.2,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 }, rectRadius: 0.08,
  });
  s.addText("Approach", {
    x: 7.1, y: 4.15, w: 5.6, h: 0.35,
    fontFace: FONT_H, fontSize: 14, bold: true, color: MINT, margin: 0,
  });
  s.addText([
    { text: "Face stream:  MTCNN  ->  ResNet-18", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Image stream:  frozen ResNet-50  +  MLP head", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Late fusion MLP (face_probs + image_probs + num_faces + flag)", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Extra credit:  CLIP image+text multimodal", options: { bullet: true, color: PAPER } },
  ], {
    x: 7.1, y: 4.55, w: 5.7, h: 1.65,
    fontFace: FONT_B, fontSize: 11.5, paraSpaceAfter: 4, margin: 0,
  });

  footer(s, 2, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 3 - PIPELINE & STATUS
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "7-Notebook Pipeline & Current Status", "02  /  PIPELINE");

  const nbs = [
    ["01", "Dataset prep",         "DONE",        "0F9D58"],
    ["02", "Face extraction",      "DONE",        "0F9D58"],
    ["03", "Face model (ResNet-18)", "DONE",      "0F9D58"],
    ["04", "Augmentation & robustness", "RUNNING", CORAL],
    ["05", "Full-image ResNet-50", "PENDING",     MUTED],
    ["06", "Late-fusion MLP",      "PENDING",     MUTED],
    ["07", "CLIP multimodal (extra)", "PENDING",  MUTED],
  ];

  // Lay out as 7 cards in a row
  const startX = 0.5, top = 1.7;
  const cardW = 1.74, cardH = 2.2, gap = 0.06;
  nbs.forEach((nb, i) => {
    const [num, name, status, statusColor] = nb;
    const x = startX + i * (cardW + gap);

    // card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: top, w: cardW, h: cardH,
      fill: { color: PAPER }, line: { color: RULE, width: 1 },
    });
    // top accent
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: top, w: cardW, h: 0.08, fill: { color: statusColor }, line: { color: statusColor, width: 0 },
    });
    // notebook number
    s.addText(num, {
      x, y: top + 0.2, w: cardW, h: 0.5,
      fontFace: FONT_H, fontSize: 26, bold: true, color: NAVY, align: "center", margin: 0,
    });
    // notebook name
    s.addText(name, {
      x: x + 0.1, y: top + 0.78, w: cardW - 0.2, h: 0.85,
      fontFace: FONT_B, fontSize: 11, color: INK, align: "center", valign: "top", margin: 0,
    });
    // status pill
    pill(s, x + 0.18, top + 1.7, cardW - 0.36, 0.32, status, statusColor, PAPER);
  });

  // Arrow connectors are visually noisy with 7 cards; substitute progress bar.
  // Big progress summary below
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.4, w: 12.3, h: 0.5,
    fill: { color: LIGHT }, line: { color: RULE, width: 1 },
  });
  // Filled portion: 3.5 / 7 done (3 done + 0.5 in-progress)
  const fillW = (3.5 / 7) * 12.3;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.4, w: fillW, h: 0.5, fill: { color: TEAL }, line: { color: TEAL, width: 0 },
  });
  s.addText("3 of 7 notebooks complete   |   1 currently running   |   3 remaining", {
    x: 0.5, y: 4.4, w: 12.3, h: 0.5,
    fontFace: FONT_H, fontSize: 13, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0,
  });

  // Three insight callouts beneath
  const callouts = [
    ["Scene-level split", "70 / 15 / 15 stratified on scene_id (seed 42) - no dialogue context leaks across splits."],
    ["Multi-face policy", "Each detected face stored separately; per-face softmax mean-pooled to image level."],
    ["No-face fallback",  "face_detected_flag=0 -> fusion MLP falls back on a neutral training-prior."],
  ];
  callouts.forEach(([h, body], i) => {
    const x = 0.5 + i * 4.15;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 5.2, w: 0.06, h: 1.55, fill: { color: TEAL }, line: { color: TEAL, width: 0 },
    });
    s.addText(h, {
      x: x + 0.18, y: 5.2, w: 3.85, h: 0.4,
      fontFace: FONT_H, fontSize: 13, bold: true, color: NAVY, margin: 0,
    });
    s.addText(body, {
      x: x + 0.18, y: 5.55, w: 3.85, h: 1.2,
      fontFace: FONT_B, fontSize: 10.5, color: INK, margin: 0,
    });
  });

  footer(s, 3, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 4 - WHAT'S DONE (NOTEBOOKS 01-03)
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "What We Have Completed (Notebooks 01 - 03)", "03  /  PROGRESS");

  const cards = [
    {
      num: "01",
      title: "Dataset Preparation",
      owner: "Sameer",
      bullets: [
        "Built the unified msctd_master.csv (En-De pooled)",
        "Stratified 70/15/15 SCENE-level split (seed 42)",
        "EDA plots: class dist, split dist, sample faces, text length",
      ],
      artefact: "data/processed/msctd_master.csv",
    },
    {
      num: "02",
      title: "Face Extraction (MTCNN)",
      owner: "Harshitha",
      bullets: [
        "facenet-pytorch MTCNN over every image",
        "224x224 face crops -> data/faces/",
        "Captured num_faces and face_detected_flag per image",
      ],
      artefact: "data/processed/face_metadata.csv",
    },
    {
      num: "03",
      title: "Face Model (ResNet-18)",
      owner: "Harshitha",
      bullets: [
        "ResNet-18, class-weighted CE, 15 epochs, lr 1e-4",
        "Test set (n=6,564 face crops):  acc 0.382  /  macro-F1 0.378",
        "Best class neutral (F1 0.42), worst positive (F1 0.32)",
      ],
      artefact: "outputs/model_checkpoints/face_resnet18.pth",
    },
  ];

  cards.forEach((c, i) => {
    const x = 0.5 + i * 4.18;
    const y = 1.6;
    const w = 4.0;
    const h = 5.3;

    // card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h, fill: { color: PAPER }, line: { color: RULE, width: 1 },
      shadow: { type: "outer", blur: 8, offset: 2, angle: 90, color: "000000", opacity: 0.06 },
    });
    // header bar
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.9, fill: { color: NAVY }, line: { color: NAVY, width: 0 },
    });
    s.addText(c.num, {
      x: x + 0.2, y: y + 0.1, w: 0.9, h: 0.7,
      fontFace: FONT_H, fontSize: 32, bold: true, color: MINT, margin: 0,
    });
    s.addText(c.title, {
      x: x + 1.1, y: y + 0.18, w: w - 1.2, h: 0.35,
      fontFace: FONT_H, fontSize: 14, bold: true, color: PAPER, margin: 0,
    });
    s.addText("Lead: " + c.owner, {
      x: x + 1.1, y: y + 0.5, w: w - 1.2, h: 0.3,
      fontFace: FONT_B, fontSize: 11, italic: true, color: MINT, margin: 0,
    });

    // bullets
    s.addText(c.bullets.map((b, j) => ({
      text: b, options: { bullet: true, breakLine: j !== c.bullets.length - 1 },
    })), {
      x: x + 0.25, y: y + 1.05, w: w - 0.5, h: 3.2,
      fontFace: FONT_B, fontSize: 11.5, color: INK, paraSpaceAfter: 8, margin: 0,
    });

    // artefact strip
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: y + h - 0.85, w, h: 0.85, fill: { color: LIGHT }, line: { color: LIGHT, width: 0 },
    });
    s.addText("KEY OUTPUT", {
      x: x + 0.25, y: y + h - 0.78, w: w - 0.5, h: 0.25,
      fontFace: FONT_H, fontSize: 9, bold: true, color: TEAL, charSpacing: 4, margin: 0,
    });
    s.addText(c.artefact, {
      x: x + 0.25, y: y + h - 0.5, w: w - 0.5, h: 0.4,
      fontFace: "Consolas", fontSize: 10, color: INK, margin: 0,
    });
  });

  footer(s, 4, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 5 - CURRENTLY RUNNING (NOTEBOOK 04)
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "Currently Running - Notebook 04: Augmentation & Robustness", "04  /  IN PROGRESS");

  // Left: experiment description
  s.addText("Three-experiment robustness study", {
    x: 0.5, y: 1.6, w: 6.5, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY, margin: 0,
  });
  s.addText("Lead: Sai Teja (with Harshitha for the face checkpoint)", {
    x: 0.5, y: 2.0, w: 6.5, h: 0.35,
    fontFace: FONT_B, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });

  // experiment rows
  const exps = [
    ["A", "Train original  ->  test original", "Baseline (NB03)", "DONE",   "0F9D58"],
    ["B", "Train original  ->  test degraded", "Drop quantified", "DONE",   "0F9D58"],
    ["C", "Train mixed (orig + degraded)  ->  test both", "Eval pending", "TODAY", CORAL],
  ];

  let ey = 2.5;
  exps.forEach(([code, desc, sub, status, color]) => {
    // letter circle
    s.addShape(pres.shapes.OVAL, {
      x: 0.5, y: ey, w: 0.55, h: 0.55, fill: { color: color }, line: { color: color, width: 0 },
    });
    s.addText(code, {
      x: 0.5, y: ey, w: 0.55, h: 0.55,
      fontFace: FONT_H, fontSize: 18, bold: true, color: PAPER, align: "center", valign: "middle", margin: 0,
    });
    s.addText(desc, {
      x: 1.2, y: ey - 0.02, w: 4.4, h: 0.32,
      fontFace: FONT_H, fontSize: 12.5, bold: true, color: INK, margin: 0,
    });
    s.addText(sub, {
      x: 1.2, y: ey + 0.28, w: 4.4, h: 0.3,
      fontFace: FONT_B, fontSize: 11, color: MUTED, italic: true, margin: 0,
    });
    pill(s, 5.7, ey + 0.07, 1.0, 0.4, status, color, PAPER);
    ey += 0.85;
  });

  // Degradation taxonomy strip
  s.addText("Degradation families (severities 0.25 / 0.50 / 0.75)", {
    x: 0.5, y: 5.35, w: 6.5, h: 0.35,
    fontFace: FONT_H, fontSize: 13, bold: true, color: NAVY, margin: 0,
  });
  s.addText([
    { text: "Frequency:  ", options: { bold: true } },
    { text: "Gaussian blur, additive noise", options: { breakLine: true } },
    { text: "Spatial:  ", options: { bold: true } },
    { text: "downscale, perspective, rotation", options: { breakLine: true } },
    { text: "Brightness:  ", options: { bold: true } },
    { text: "exposure shift, gamma" },
  ], {
    x: 0.5, y: 5.7, w: 6.5, h: 1.3,
    fontFace: FONT_B, fontSize: 11.5, color: INK, paraSpaceAfter: 4, margin: 0,
  });

  // Right: result table card
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.4, y: 1.55, w: 5.5, h: 5.4,
    fill: { color: NAVY }, line: { color: NAVY, width: 0 },
  });
  s.addText("Results so far (face-level, n=6,564)", {
    x: 7.6, y: 1.65, w: 5.1, h: 0.4,
    fontFace: FONT_H, fontSize: 13, bold: true, color: MINT, margin: 0,
  });

  // Table
  const tblHeader = (t) => ({ text: t, options: { bold: true, fill: { color: TEAL }, color: PAPER, align: "center", fontSize: 10.5 } });
  const tblCell   = (t, opts={}) => ({ text: t, options: Object.assign({ color: PAPER, align: "center", fontSize: 11 }, opts) });
  s.addTable([
    [ tblHeader("Experiment"), tblHeader("Accuracy"), tblHeader("Macro-F1"), tblHeader("Status") ],
    [ tblCell("A  orig -> orig"),   tblCell("0.382"), tblCell("0.378"), tblCell("done", { color: MINT, bold: true }) ],
    [ tblCell("B  orig -> degraded"), tblCell("0.357"), tblCell("0.322"), tblCell("done", { color: MINT, bold: true }) ],
    [ tblCell("C  mixed -> orig"),  tblCell("---"),   tblCell("---"),   tblCell("running", { color: CORAL, bold: true }) ],
    [ tblCell("C  mixed -> degraded"), tblCell("---"), tblCell("---"),  tblCell("running", { color: CORAL, bold: true }) ],
  ], {
    x: 7.6, y: 2.1, w: 5.1, colW: [1.7, 1.1, 1.1, 1.2],
    rowH: 0.4, border: { type: "solid", pt: 0.5, color: TEAL },
  });

  // Insight box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.6, y: 4.4, w: 5.1, h: 2.4,
    fill: { color: NAVY }, line: { color: MINT, width: 1 },
  });
  s.addText("Key finding so far", {
    x: 7.75, y: 4.5, w: 4.9, h: 0.35,
    fontFace: FONT_H, fontSize: 12, bold: true, color: MINT, charSpacing: 4, margin: 0,
  });
  s.addText([
    { text: "Under degradation the unaugmented model collapses toward 'negative':  recall jumps to 0.70 while neutral/positive recall fall to ~0.18-0.20.", options: { breakLine: true, bullet: true, color: PAPER } },
    { text: "This motivates Experiment C - augmented training should restore neutral/positive recall without losing original-test performance.", options: { bullet: true, color: PAPER } },
  ], {
    x: 7.75, y: 4.85, w: 4.9, h: 1.85,
    fontFace: FONT_B, fontSize: 11, paraSpaceAfter: 6, margin: 0,
  });

  footer(s, 5, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 6 - INITIAL RESULTS CHART
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "Initial Quantitative Results", "05  /  RESULTS");

  // Per-class F1 chart for face_resnet18 (NB03)
  s.addText("Per-class F1  -  face_resnet18 on the held-out test split", {
    x: 0.5, y: 1.6, w: 8.5, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: NAVY, margin: 0,
  });

  s.addChart(pres.charts.BAR, [
    {
      name: "Test on original",
      labels: ["negative", "neutral", "positive"],
      values: [0.389, 0.423, 0.323],
    },
    {
      name: "Test on degraded",
      labels: ["negative", "neutral", "positive"],
      values: [0.464, 0.243, 0.260],
    },
  ], {
    x: 0.5, y: 2.05, w: 8.5, h: 4.5, barDir: "col",
    chartColors: [TEAL, CORAL],
    chartArea: { fill: { color: PAPER } },
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 11,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 10,
    valAxisMinVal: 0, valAxisMaxVal: 0.55,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd",
    dataLabelColor: INK, dataLabelFontSize: 9,
    showLegend: true, legendPos: "t", legendFontSize: 10, legendColor: INK,
    showTitle: false,
  });

  // Right takeaways column
  s.addShape(pres.shapes.RECTANGLE, {
    x: 9.4, y: 1.6, w: 3.5, h: 5.3, fill: { color: LIGHT }, line: { color: RULE, width: 1 },
  });
  s.addText("Takeaways", {
    x: 9.55, y: 1.7, w: 3.2, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: NAVY, margin: 0,
  });

  s.addText([
    { text: "Face-only is weak (acc 0.382) - by design: scene context is missing.", options: { bullet: true, breakLine: true } },
    { text: "Neutral wins on original images; collapses under degradation.", options: { bullet: true, breakLine: true } },
    { text: "Negative recall spikes to 0.70 on degraded data: model is over-predicting one class.", options: { bullet: true, breakLine: true } },
    { text: "Macro-F1 drops 0.378  ->  0.322  =  -15% relative.", options: { bullet: true, breakLine: true } },
    { text: "Augmented training (Exp C) and the full-image / fusion stages are designed to close these gaps.", options: { bullet: true } },
  ], {
    x: 9.55, y: 2.1, w: 3.2, h: 4.7,
    fontFace: FONT_B, fontSize: 10.5, color: INK, paraSpaceAfter: 7, margin: 0,
  });

  footer(s, 6, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 7 - TASK DISTRIBUTION
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "Task Distribution Across the Group", "06  /  WHO DOES WHAT");

  s.addText("Each member owns one stage end-to-end - but every member must understand the whole pipeline (oral exam = 40%).", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.45,
    fontFace: FONT_B, fontSize: 12, italic: true, color: MUTED, margin: 0,
  });

  const headerOpt = { fill: { color: NAVY }, color: PAPER, bold: true, align: "left", fontSize: 11.5, valign: "middle" };
  const rowOpt = (alt) => ({ fill: { color: alt ? LIGHT : PAPER }, color: INK, fontSize: 11, valign: "middle" });

  const rows = [
    [
      { text: "Shaik Sameer",          options: { ...rowOpt(false), bold: true, color: NAVY } },
      { text: "6944091",                options: rowOpt(false) },
      { text: "Dataset prep, repo & log management", options: rowOpt(false) },
      { text: "Notebook 01",            options: rowOpt(false) },
      { text: "msctd_master.csv, EDA plots, GitHub repo, weekly logs", options: rowOpt(false) },
    ],
    [
      { text: "Ammineni Harshitha",     options: { ...rowOpt(true), bold: true, color: NAVY } },
      { text: "6952560",                options: rowOpt(true) },
      { text: "Face extraction & face model",       options: rowOpt(true) },
      { text: "Notebooks 02, 03",       options: rowOpt(true) },
      { text: "face_metadata.csv, face_resnet18.pth, predictions, CMs", options: rowOpt(true) },
    ],
    [
      { text: "Tharigopula Sai Teja",   options: { ...rowOpt(false), bold: true, color: NAVY } },
      { text: "6945944",                options: rowOpt(false) },
      { text: "Augmentation & robustness experiments", options: rowOpt(false) },
      { text: "Notebook 04",            options: rowOpt(false) },
      { text: "degraded_faces/, face_resnet18_augmented.pth, robustness table", options: rowOpt(false) },
    ],
    [
      { text: "Kakumanu Ravi Teja",     options: { ...rowOpt(true), bold: true, color: NAVY } },
      { text: "6905377",                options: rowOpt(true) },
      { text: "Full-image transfer-learning model",  options: rowOpt(true) },
      { text: "Notebook 05",            options: rowOpt(true) },
      { text: "full_image_resnet50_mlp.pth, image-level metrics", options: rowOpt(true) },
    ],
    [
      { text: "Mosi Curran",            options: { ...rowOpt(false), bold: true, color: NAVY } },
      { text: "6946833",                options: rowOpt(false) },
      { text: "Fusion model + multimodal CLIP (extra credit)", options: rowOpt(false) },
      { text: "Notebooks 06, 07",       options: rowOpt(false) },
      { text: "fusion_mlp.pth, clip_multimodal_classifier.pth, final_model_comparison.csv", options: rowOpt(false) },
    ],
  ];

  s.addTable([
    [
      { text: "Member",        options: { ...headerOpt, fill: { color: NAVY } } },
      { text: "Student ID",    options: headerOpt },
      { text: "Primary focus", options: headerOpt },
      { text: "Notebook(s)",   options: headerOpt },
      { text: "Key artefacts", options: headerOpt },
    ],
    ...rows,
  ], {
    x: 0.5, y: 2.1, w: 12.3,
    colW: [2.5, 1.2, 3.0, 1.6, 4.0], rowH: 0.62,
    border: { type: "solid", pt: 0.5, color: RULE },
    fontFace: FONT_B,
  });

  footer(s, 7, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 8 - REMAINING WORK & DEADLINES
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "What Each Person Will Finish & By When", "07  /  TIMELINE");

  // Timeline canvas
  const tlX = 0.6, tlY = 2.0, tlW = 12.0;
  const weeks = ["Now\n25 Apr", "Week 11\n2 May", "Week 12\n9 May", "Week 13\n16 May", "Final\n23 May"];
  const colW = tlW / weeks.length;

  // axis line
  s.addShape(pres.shapes.LINE, {
    x: tlX, y: tlY + 0.55, w: tlW, h: 0,
    line: { color: RULE, width: 1 },
  });

  weeks.forEach((label, i) => {
    const cx = tlX + i * colW;
    // tick
    s.addShape(pres.shapes.LINE, {
      x: cx, y: tlY + 0.5, w: 0, h: 0.12, line: { color: MUTED, width: 1 },
    });
    s.addText(label, {
      x: cx - 0.5, y: tlY, w: 1.0, h: 0.5,
      fontFace: FONT_H, fontSize: 10.5, bold: true, color: NAVY, align: "center", margin: 0,
    });
  });

  // Bars: [owner, label, startCol, span, color, deliverable]
  const tasks = [
    { who: "Sai Teja",        what: "NB04  -  finish Experiment C eval + robustness table", start: 0,    span: 1.0, color: CORAL, due: "Wed 30 Apr" },
    { who: "Ravi Teja",       what: "NB05  -  full-image ResNet-50 + MLP head training",     start: 0.7,  span: 1.6, color: TEAL,  due: "Wed 7 May"  },
    { who: "Mosi Curran",     what: "NB06  -  late-fusion MLP + final comparison",            start: 1.8,  span: 1.4, color: TEAL,  due: "Wed 14 May" },
    { who: "Mosi Curran",     what: "NB07  -  CLIP multimodal (extra credit)",                start: 2.6,  span: 1.4, color: MINT,  due: "Wed 21 May" },
    { who: "Harshitha + Sai", what: "Re-run face training with best aug. config (if time)",   start: 1.0,  span: 1.0, color: MUTED, due: "Mon 12 May" },
    { who: "Sameer",          what: "Repo hygiene, weekly logs, README, viva-prep",           start: 0.0,  span: 5.0, color: NAVY,  due: "Continuous" },
    { who: "All",             what: "IEEE report draft  +  final 5-min slides",               start: 3.5,  span: 1.5, color: NAVY,  due: "Fri 23 May" },
  ];

  const rowH = 0.45, rowGap = 0.12;
  const barTop = tlY + 0.95;
  tasks.forEach((t, i) => {
    const yRow = barTop + i * (rowH + rowGap);
    // owner label (left gutter)
    s.addText(t.who, {
      x: 0, y: yRow, w: tlX - 0.05, h: rowH,
      fontFace: FONT_H, fontSize: 9.5, bold: true, color: NAVY, align: "right", valign: "middle", margin: 0,
    });

    // bar
    const barX = tlX + t.start * colW;
    const barW = Math.min(t.span * colW, tlW - t.start * colW);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: barX, y: yRow, w: barW, h: rowH,
      fill: { color: t.color }, line: { color: t.color, width: 0 }, rectRadius: 0.05,
    });
    s.addText(t.what, {
      x: barX + 0.1, y: yRow, w: barW - 0.2, h: rowH,
      fontFace: FONT_B, fontSize: 9.5, bold: true, color: PAPER, valign: "middle", margin: 0,
    });
    // due badge to the right of bar (if room)
    const dueX = barX + barW + 0.1;
    if (dueX < 12.7) {
      s.addText("due " + t.due, {
        x: dueX, y: yRow, w: 12.7 - dueX, h: rowH,
        fontFace: FONT_B, fontSize: 9, italic: true, color: MUTED, valign: "middle", margin: 0,
      });
    }
  });

  // legend
  const legY = 6.85;
  const legend = [
    ["This week", CORAL],
    ["Core deliverable", TEAL],
    ["Extra credit", MINT],
    ["Continuous / shared", NAVY],
  ];
  let lx = 0.6;
  legend.forEach(([lab, col]) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: lx, y: legY + 0.05, w: 0.18, h: 0.18, fill: { color: col }, line: { color: col, width: 0 },
    });
    s.addText(lab, {
      x: lx + 0.25, y: legY, w: 2.5, h: 0.3, fontFace: FONT_B, fontSize: 10, color: MUTED, valign: "middle", margin: 0,
    });
    lx += 2.6;
  });

  footer(s, 8, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 9 - GITHUB & LOGS
// =====================================================================
{
  const s = pres.addSlide();
  pageHeader(s, "GitHub Activity, Weekly Logs & Reproducibility", "08  /  PROCESS");

  // Three columns
  const cols = [
    {
      title: "GitHub repository",
      colour: TEAL,
      lines: [
        "Repo: EEEM068-Human-Sentiment-Analysis (private)",
        "Instructor 'elsobhano' invited as collaborator",
        "Branching: feature/<name>-<topic>  ->  PR  ->  main",
        "Conventional commits, e.g.  feat(nb03): face model first pass",
      ],
    },
    {
      title: "Weekly logs (logs/week_N/)",
      colour: NAVY,
      lines: [
        "One <name>_log.md per member, every week from week 7",
        "Records: tasks, commits, hyperparameters, results, blockers",
        "Commit message form:  logs(week_N): <name> - <summary>",
        "TA / Sobhan can audit individual contribution from logs + git",
      ],
    },
    {
      title: "Reproducibility",
      colour: MINT,
      lines: [
        "Single config in src/config.py (paths, seeds, hyperparams)",
        "src.utils.seed_everything(42) at the top of every notebook",
        "Outputs versioned in outputs/ ; checkpoints in model_checkpoints/",
        "scripts/setup_data.* for one-click data download + verify",
      ],
    },
  ];

  cols.forEach((c, i) => {
    const x = 0.5 + i * 4.18;
    const y = 1.7;
    const w = 4.0;
    const h = 4.6;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.6, fill: { color: c.colour }, line: { color: c.colour, width: 0 },
    });
    s.addText(c.title, {
      x: x + 0.2, y, w: w - 0.3, h: 0.6,
      fontFace: FONT_H, fontSize: 14, bold: true, color: PAPER, valign: "middle", margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: y + 0.6, w, h: h - 0.6, fill: { color: PAPER }, line: { color: RULE, width: 1 },
    });
    s.addText(c.lines.map((l, j) => ({
      text: l, options: { bullet: true, breakLine: j !== c.lines.length - 1 },
    })), {
      x: x + 0.25, y: y + 0.75, w: w - 0.5, h: h - 0.85,
      fontFace: FONT_B, fontSize: 11.5, color: INK, paraSpaceAfter: 8, margin: 0,
    });
  });

  // Bottom action card
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.5, w: 12.3, h: 0.55, fill: { color: NAVY }, line: { color: NAVY, width: 0 }, rectRadius: 0.06,
  });
  s.addText([
    { text: "Action this week:  ", options: { bold: true, color: MINT } },
    { text: "every member commits at least one weekly log + one feature branch PR. Lab-hours check-in with Dr. Asasi to confirm direction.", options: { color: PAPER } },
  ], {
    x: 0.7, y: 6.5, w: 12.0, h: 0.55,
    fontFace: FONT_B, fontSize: 12, valign: "middle", margin: 0,
  });

  footer(s, 9, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 10 - RISKS, ASKS & THANK YOU
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // accent bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: MINT }, line: { color: MINT, width: 0 },
  });

  s.addText("09  /  CLOSING", {
    x: 0.9, y: 0.5, w: 11, h: 0.4,
    fontFace: FONT_H, fontSize: 12, bold: true, color: MINT, charSpacing: 8, margin: 0,
  });
  s.addText("Risks, Asks & Thank You", {
    x: 0.9, y: 0.85, w: 11, h: 0.7,
    fontFace: FONT_H, fontSize: 32, bold: true, color: PAPER, margin: 0,
  });

  // Two columns: Risks  |  Asks
  s.addText("Top risks we are tracking", {
    x: 0.9, y: 1.85, w: 5.8, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: MINT, margin: 0,
  });
  s.addText([
    { text: "CPU-only training: NB04-07 each take hours; we have planned around it but slip risk is real.", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Face model is barely above chance on its own; the value comes from fusion in NB06.", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Class imbalance + many neutral mild expressions may cap performance on neutral.", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "MSCTD images sometimes contain no detectable face -> we rely on the no-face fallback path.", options: { bullet: true, color: PAPER } },
  ], {
    x: 0.9, y: 2.3, w: 5.8, h: 4.5,
    fontFace: FONT_B, fontSize: 12, color: PAPER, paraSpaceAfter: 8, margin: 0,
  });

  s.addText("Asks for the instructor", {
    x: 7.0, y: 1.85, w: 5.8, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: MINT, margin: 0,
  });
  s.addText([
    { text: "Confirm scope of the 'extra credit' multimodal CLIP task is acceptable as Notebook 07.", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Sign-off on the late-fusion architecture (face_probs + image_probs + num_faces + flag).", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Lab-hours slot to walk through the face-model error analysis.", options: { bullet: true, breakLine: true, color: PAPER } },
    { text: "Confirm GitHub access (elsobhano) - if not visible, please flag so we can re-invite.", options: { bullet: true, color: PAPER } },
  ], {
    x: 7.0, y: 2.3, w: 5.8, h: 4.5,
    fontFace: FONT_B, fontSize: 12, color: PAPER, paraSpaceAfter: 8, margin: 0,
  });

  // Thank-you strip
  s.addShape(pres.shapes.LINE, {
    x: 0.9, y: 6.6, w: 12.0, h: 0,
    line: { color: MINT, width: 2 },
  });
  s.addText("Thank you  -  questions welcome.", {
    x: 0.9, y: 6.7, w: 7.0, h: 0.5,
    fontFace: FONT_H, fontSize: 18, bold: true, color: PAPER, margin: 0,
  });
  s.addText("Sameer  /  Harshitha  /  Sai Teja  /  Ravi Teja  /  Mosi", {
    x: 7.9, y: 6.78, w: 5.0, h: 0.4,
    fontFace: FONT_B, fontSize: 11, italic: true, color: "C8D6E5", align: "right", margin: 0,
  });
}

// ---------- Write ----------
pres.writeFile({ fileName: "progress_presentation.pptx" }).then((f) => {
  console.log("Wrote: " + f);
});
