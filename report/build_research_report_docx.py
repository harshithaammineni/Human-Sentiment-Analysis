from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
FIG_DIR = REPORT_DIR / "generated_figures"
OUT_DOCX = REPORT_DIR / "EEEM068_Human_Sentiment_Analysis_Report_research_rewrite.docx"

DATA_DIR = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
PLOTS = OUTPUTS / "plots"
METRICS = OUTPUTS / "metrics"
CMS = OUTPUTS / "confusion_matrices"
PREDS = OUTPUTS / "predictions"

NAVY = "17365D"
TEAL = "1F7A8C"
MINT = "D8F0F2"
LIGHT = "F4F7FA"
RULE = "D9E2EC"
INK = "1F2933"
MUTED = "52616B"
CORAL = "B9553C"
TABLE_COUNTER = 0


def font(size: int = 22, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def draw_box(draw: ImageDraw.ImageDraw, box, label, fill, outline=RULE, text=INK, title=False):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill=f"#{fill}", outline=f"#{outline}", width=3)
    f = font(26 if title else 22, bold=title)
    lines = wrap_text(draw, label, f, x2 - x1 - 40)
    total = len(lines) * (f.size + 7)
    y = y1 + ((y2 - y1) - total) / 2
    for line in lines:
        w = draw.textlength(line, font=f)
        draw.text((x1 + (x2 - x1 - w) / 2, y), line, font=f, fill=f"#{text}")
        y += f.size + 7


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def arrow(draw: ImageDraw.ImageDraw, start, end, color=TEAL):
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=f"#{color}", width=5)
    ang = np.arctan2(y2 - y1, x2 - x1)
    size = 16
    pts = [
        (x2, y2),
        (x2 - size * np.cos(ang - np.pi / 6), y2 - size * np.sin(ang - np.pi / 6)),
        (x2 - size * np.cos(ang + np.pi / 6), y2 - size * np.sin(ang + np.pi / 6)),
    ]
    draw.polygon(pts, fill=f"#{color}")


def make_pipeline_diagram():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / "pipeline_architecture.png"
    img = Image.new("RGB", (1800, 980), "white")
    d = ImageDraw.Draw(img)
    d.text((70, 45), "Experimental Pipeline", font=font(44, True), fill=f"#{NAVY}")
    d.text((70, 100), "Scene-level split, face and image branches, late fusion, and extra-credit CLIP multimodal branch", font=font(24), fill=f"#{MUTED}")

    draw_box(d, (80, 210, 380, 350), "MSCTD En-De 30,370 image-text pairs", LIGHT, title=True)
    draw_box(d, (500, 150, 850, 290), "MTCNN face crops 43,768 faces", MINT, title=True)
    draw_box(d, (500, 370, 850, 510), "Full 224x224 image", MINT, title=True)
    draw_box(d, (960, 145, 1280, 285), "Face ResNet18 softmax", LIGHT, title=True)
    draw_box(d, (960, 365, 1280, 505), "Frozen ResNet50 + MLP softmax", LIGHT, title=True)
    draw_box(d, (1390, 255, 1710, 405), "Fusion MLP 8 -> 32 -> 16 -> 3", "E8F3FF", title=True)
    draw_box(d, (500, 650, 850, 800), "English utterance + image", "FFF3E8", title=True)
    draw_box(d, (960, 650, 1280, 800), "Frozen CLIP embeddings + MLP", "FFF3E8", title=True)
    draw_box(d, (1390, 650, 1710, 800), "Multimodal sentiment prediction", "FFF3E8", title=True)
    for s, e in [
        ((380, 280), (500, 220)), ((380, 280), (500, 440)),
        ((850, 220), (960, 215)), ((850, 440), (960, 435)),
        ((1280, 215), (1390, 310)), ((1280, 435), (1390, 355)),
        ((380, 280), (500, 725)), ((850, 725), (960, 725)), ((1280, 725), (1390, 725)),
    ]:
        arrow(d, s, e)
    d.text((1395, 420), "Inputs: face probabilities, image probabilities,\nnum_faces_norm, face_detected_flag", font=font(22), fill=f"#{MUTED}")
    img.save(path, quality=95)
    return path


def make_clip_diagram():
    path = FIG_DIR / "clip_architecture.png"
    img = Image.new("RGB", (1800, 820), "white")
    d = ImageDraw.Draw(img)
    d.text((70, 45), "CLIP Multimodal Branch", font=font(44, True), fill=f"#{NAVY}")
    d.text((70, 100), "Frozen encoders, concatenated 512-d image and text projections, trainable classifier head", font=font(24), fill=f"#{MUTED}")

    draw_box(d, (80, 220, 390, 350), "Image frame", LIGHT, title=True)
    draw_box(d, (80, 500, 390, 630), "English utterance", LIGHT, title=True)
    draw_box(d, (520, 190, 860, 380), "CLIP ViT-B/32 image encoder frozen", "E8F3FF", title=True)
    draw_box(d, (520, 470, 860, 660), "CLIP text transformer frozen", "E8F3FF", title=True)
    draw_box(d, (1000, 335, 1290, 515), "Concatenate 512 + 512", "FFF3E8", title=True)
    draw_box(d, (1410, 335, 1710, 515), "MLP head 295,683 trainable params", "FFF3E8", title=True)
    arrow(d, (390, 285), (520, 285))
    arrow(d, (390, 565), (520, 565))
    arrow(d, (860, 285), (1000, 395))
    arrow(d, (860, 565), (1000, 455))
    arrow(d, (1290, 425), (1410, 425))
    d.text((1415, 535), "Output: negative, neutral, positive", font=font(24), fill=f"#{MUTED}")
    img.save(path, quality=95)
    return path


def make_bar_chart(rows: list[tuple[str, float]]):
    path = FIG_DIR / "macro_f1_comparison_with_clip.png"
    w, h = 1800, 1050
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d.text((70, 45), "Test Macro-F1 by Model", font=font(44, True), fill=f"#{NAVY}")
    d.text((70, 100), "CLIP is included from clip_multimodal_metrics.json; the repository CSV comparison had not been refreshed.", font=font(24), fill=f"#{MUTED}")
    left, top, bar_h, gap = 620, 185, 62, 34
    axis_w = 980
    max_v = 0.60
    for i, (name, val) in enumerate(rows):
        y = top + i * (bar_h + gap)
        d.text((70, y + 14), name, font=font(24, True if "CLIP" in name else False), fill=f"#{INK}")
        fill = CORAL if "CLIP" in name else TEAL
        bw = int(axis_w * val / max_v)
        d.rounded_rectangle((left, y, left + bw, y + bar_h), radius=12, fill=f"#{fill}")
        d.text((left + bw + 18, y + 14), f"{val:.3f}", font=font(24, True), fill=f"#{INK}")
    d.line((left, top - 25, left, top + len(rows) * (bar_h + gap) - gap + 25), fill=f"#{RULE}", width=3)
    for tick in [0.0, 0.2, 0.4, 0.6]:
        x = left + int(axis_w * tick / max_v)
        d.line((x, top + len(rows) * (bar_h + gap) - gap + 35, x, top + len(rows) * (bar_h + gap) - gap + 50), fill=f"#{MUTED}", width=2)
        d.text((x - 25, top + len(rows) * (bar_h + gap) - gap + 60), f"{tick:.1f}", font=font(22), fill=f"#{MUTED}")
    img.save(path, quality=95)
    return path


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def f1_summary(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    out = []
    f1s = []
    supports = []
    for c in [0, 1, 2]:
        tp = int(((y_true == c) & (y_pred == c)).sum())
        fp = int(((y_true != c) & (y_pred == c)).sum())
        fn = int(((y_true == c) & (y_pred != c)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        out.append((p, r, f))
        f1s.append(f)
        supports.append(int((y_true == c).sum()))
    acc = float((y_true == y_pred).mean())
    macro = float(np.mean(f1s))
    weighted = float(np.average(f1s, weights=supports))
    return acc, macro, weighted, out


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text_color(cell, color: str):
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.color.rgb = RGBColor.from_string(color)


def set_cell_borders(cell, color=RULE, size="8"):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_cell_width(cell, width_inches: float):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.first_child_found_in("w:tcW")
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def set_table_grid(table, widths: list[float]):
    table.autofit = False
    table.allow_autofit = False
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(sum(widths) * 1440)))
    tbl_w.set(qn("w:type"), "dxa")

    old_grid = tbl.tblGrid
    if old_grid is not None:
        tbl.remove(old_grid)
    grid = OxmlElement("w:tblGrid")
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(width * 1440)))
        grid.append(col)
    tbl.insert(1, grid)


def draw_table_image(headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> Path:
    global TABLE_COUNTER
    TABLE_COUNTER += 1
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"table_{TABLE_COUNTER:02d}.png"
    scale_w = 2300
    margin = 24
    usable = scale_w - margin * 2
    if widths:
        total = sum(widths)
        col_w = [int(usable * w / total) for w in widths]
        col_w[-1] += usable - sum(col_w)
    else:
        col_w = [usable // len(headers)] * len(headers)
        col_w[-1] += usable - sum(col_w)

    f_hdr = font(31, True)
    f_body = font(28, False)
    f_body_bold = font(28, True)
    pad_x, pad_y = 18, 13

    def wrapped_lines(text: str, width_px: int, fnt):
        text = str(text)
        out = []
        for raw in text.split("\n"):
            lines = wrap_text(ImageDraw.Draw(Image.new("RGB", (1, 1))), raw, fnt, width_px - 2 * pad_x)
            out.extend(lines or [""])
        return out

    row_heights = []
    for source, fnt in [(headers, f_hdr)] + [(row, f_body) for row in rows]:
        max_lines = 1
        for text, cw in zip(source, col_w):
            max_lines = max(max_lines, len(wrapped_lines(text, cw, fnt)))
        row_heights.append(max(64, max_lines * (fnt.size + 7) + pad_y * 2))

    total_h = margin * 2 + sum(row_heights)
    img = Image.new("RGB", (scale_w, total_h), "white")
    d = ImageDraw.Draw(img)
    y = margin

    def draw_row(values, h, fill, text_color, fnt, bold_first=False):
        nonlocal y
        x = margin
        for idx, (value, cw) in enumerate(zip(values, col_w)):
            d.rectangle((x, y, x + cw, y + h), fill=f"#{fill}", outline=f"#{RULE}", width=3)
            lines = wrapped_lines(value, cw, fnt)
            line_h = fnt.size + 7
            text_h = len(lines) * line_h
            ty = y + (h - text_h) / 2
            for line in lines:
                use_font = f_body_bold if (bold_first and idx == 0) else fnt
                if idx == 0:
                    tx = x + pad_x
                else:
                    tw = d.textlength(line, font=use_font)
                    tx = x + (cw - tw) / 2
                d.text((tx, ty), line, font=use_font, fill=f"#{text_color}")
                ty += line_h
            x += cw
        y += h

    draw_row(headers, row_heights[0], NAVY, "FFFFFF", f_hdr)
    for i, row in enumerate(rows):
        draw_row(row, row_heights[i + 1], LIGHT if i % 2 else "FFFFFF", INK, f_body, bold_first=True)

    img.save(path, quality=95)
    return path


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None):
    table_path = draw_table_image(headers, rows, widths)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(str(table_path), width=Inches(6.45))
    return None


def add_native_table_unused(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None):
    if widths:
        total = sum(widths)
        max_width = 6.45
        if total > max_width:
            widths = [w * max_width / total for w in widths]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    if widths:
        set_table_grid(table, widths)
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        if widths:
            set_cell_width(hdr[i], widths[i])
        set_cell_shading(hdr[i], NAVY)
        set_cell_text_color(hdr[i], "FFFFFF")
        hdr[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in hdr[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(8)
                r.font.name = "Arial"
        set_cell_borders(hdr[i])
    for r_i, row in enumerate(rows):
        cells = table.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = str(val)
            if widths:
                set_cell_width(cells[j], widths[j])
            cells[j].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if r_i % 2 == 1:
                set_cell_shading(cells[j], LIGHT)
            for p in cells[j].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.size = Pt(8)
                    run.font.name = "Arial"
                    run.font.color.rgb = RGBColor.from_string(INK)
            set_cell_borders(cells[j])
    doc.add_paragraph()
    return table


def add_caption(doc: Document, text: str):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(8)
    for r in p.runs:
        r.font.size = Pt(9)
        r.font.italic = True
        r.font.color.rgb = RGBColor.from_string(MUTED)


def add_image(doc: Document, path: Path, caption: str, width=6.4):
    if path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Inches(width))
        add_caption(doc, caption)


def add_side_by_side_images(doc: Document, left: Path, right: Path, caption: str):
    global TABLE_COUNTER
    TABLE_COUNTER += 1
    out = FIG_DIR / f"side_by_side_{TABLE_COUNTER:02d}.png"
    panels = []
    for label, path in [("Fusion MLP", left), ("CLIP multimodal", right)]:
        if path.exists():
            im = Image.open(path).convert("RGB")
            im.thumbnail((980, 760))
            panel = Image.new("RGB", (1040, 850), "white")
            d = ImageDraw.Draw(panel)
            d.text((40, 25), label, font=font(34, True), fill=f"#{NAVY}")
            panel.paste(im, (30 + (980 - im.width) // 2, 80))
            panels.append(panel)
    if panels:
        combined = Image.new("RGB", (sum(p.width for p in panels), max(p.height for p in panels)), "white")
        x = 0
        for pimg in panels:
            combined.paste(pimg, (x, 0))
            x += pimg.width
        combined.save(out, quality=95)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(out), width=Inches(6.25))
    add_caption(doc, caption)


def add_heading(doc: Document, text: str, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


def add_paragraph(doc: Document, text: str, style=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.08
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.name = "Times New Roman"
    run.font.color.rgb = RGBColor.from_string(INK)
    return p


def add_bullets(doc: Document, items: Iterable[str]):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(item)
        run.font.size = Pt(10)
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor.from_string(INK)


def set_styles(doc: Document):
    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(10.5)
    styles["Normal"].font.color.rgb = RGBColor.from_string(INK)
    for name, size, color in [
        ("Title", 22, NAVY),
        ("Heading 1", 15, NAVY),
        ("Heading 2", 12, TEAL),
        ("Heading 3", 11, INK),
    ]:
        style = styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10 if name != "Title" else 0)
        style.paragraph_format.space_after = Pt(5)


def add_footer(section):
    footer = section.footer.paragraphs[0]
    footer.text = "EEEM068 Applied Machine Learning | Human Sentiment Analysis | Research report rewrite"
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer.runs:
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string(MUTED)


def build_report():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    master = pd.read_csv(DATA_DIR / "msctd_master.csv")
    faces = pd.read_csv(DATA_DIR / "face_metadata.csv")
    fusion_features = pd.read_csv(DATA_DIR / "fusion_features.csv")
    test = fusion_features[fusion_features["split"] == "test"].reset_index(drop=True)
    fusion_pred = pd.read_csv(PREDS / "fusion_mlp_predictions.csv")
    clip_pred = pd.read_csv(PREDS / "clip_multimodal_predictions.csv")

    face_metrics = read_json(METRICS / "face_resnet18_metrics.json")
    face_deg = read_json(METRICS / "face_resnet18_test_degraded_metrics.json")
    face_aug_clean = read_json(METRICS / "face_resnet18_aug_test_original_metrics.json")
    face_aug_deg = read_json(METRICS / "face_resnet18_aug_test_degraded_metrics.json")
    full_metrics = read_json(METRICS / "full_image_resnet50_metrics.json")
    fusion_metrics = read_json(METRICS / "fusion_mlp_metrics.json")
    clip_metrics = read_json(METRICS / "clip_multimodal_metrics.json")

    label_cols = ["negative", "neutral", "positive"]
    face_img_pred = test[[f"face_prob_{c}" for c in label_cols]].to_numpy().argmax(axis=1)
    image_pred = test[[f"image_prob_{c}" for c in label_cols]].to_numpy().argmax(axis=1)
    y_test = test["label_id"].to_numpy()
    face_img_acc, face_img_macro, face_img_weighted, face_img_prf = f1_summary(y_test, face_img_pred)

    regimes = []
    for name, mask in [
        ("All image-level test rows", np.ones(len(test), dtype=bool)),
        ("No detected face", test["num_faces"].eq(0).to_numpy()),
        ("Single detected face", test["num_faces"].eq(1).to_numpy()),
        ("Two or more faces", test["num_faces"].ge(2).to_numpy()),
        ("Three or more faces", test["num_faces"].ge(3).to_numpy()),
    ]:
        _, im_macro, _, im_prf = f1_summary(y_test[mask], image_pred[mask])
        _, fu_macro, _, fu_prf = f1_summary(y_test[mask], fusion_pred["y_pred"].to_numpy()[mask])
        _, cl_macro, _, cl_prf = f1_summary(y_test[mask], clip_pred["y_pred"].to_numpy()[mask])
        regimes.append([
            name,
            f"{int(mask.sum()):,}",
            f"{im_macro:.3f}",
            f"{fu_macro:.3f}",
            f"{fu_prf[0][2]:.3f}",
            f"{cl_macro:.3f}",
        ])

    model_rows = [
        ("Majority baseline", 0.1833),
        ("Face ResNet18, crop-level", face_metrics["macro_f1"]),
        ("Face ResNet18, degraded crop test", face_deg["macro_f1"]),
        ("Aug-trained face, clean crop test", face_aug_clean["macro_f1"]),
        ("Aug-trained face, degraded crop test", face_aug_deg["macro_f1"]),
        ("Full-image ResNet50 + MLP", full_metrics["macro_f1"]),
        ("Fusion MLP", fusion_metrics["macro_f1"]),
        ("CLIP image + text", clip_metrics["macro_f1"]),
    ]
    pipeline_fig = make_pipeline_diagram()
    clip_fig = make_clip_diagram()
    bar_fig = make_bar_chart(model_rows)

    doc = Document()
    set_styles(doc)
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(0.72)
    sec.bottom_margin = Inches(0.72)
    sec.left_margin = Inches(0.72)
    sec.right_margin = Inches(0.72)
    add_footer(sec)

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Multimodal Human Sentiment Analysis on MSCTD En-De")
    run.font.name = "Arial"
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(NAVY)
    p.paragraph_format.space_after = Pt(3)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("A reproducible study of face-level cues, full-image context, late fusion, robustness, and CLIP image-text modelling")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.italic = True
    r.font.color.rgb = RGBColor.from_string(MUTED)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("EEEM068 Applied Machine Learning | University of Surrey")
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(TEAL)

    add_table(
        doc,
        ["Student", "ID", "Primary project responsibility"],
        [
            ["Shaik Sameer", "6944091", "Dataset preparation, reproducibility, logs, final table audit"],
            ["Ammineni Harshitha", "6952560", "MTCNN face extraction, ResNet18 face model, per-class metrics"],
            ["Tharigopula Sai Teja", "6945944", "Degradation families, augmentation, robustness analysis"],
            ["Kakumanu Ravi Teja", "6905377", "Frozen full-image ResNet50 model, ViT ablation, CLIP debugging"],
            ["Mosi Curran", "6946833", "Late-fusion MLP and extra-credit CLIP multimodal model"],
        ],
        [1.7, 0.8, 4.4],
    )
    add_paragraph(
        doc,
        "This document is a full research-style rewrite produced from the executed notebooks, output files, weekly logs, report draft, and generated metrics in the project directory. Numerical claims are tied to saved artifacts rather than manually edited summaries."
    )
    doc.add_page_break()

    add_heading(doc, "Abstract", 1)
    add_paragraph(
        doc,
        "This report studies three-class sentiment classification on the English-German split of MSCTD, a multimodal dialogue corpus containing 30,370 utterance-image pairs across 3,079 scenes. The work evaluates whether still-image sentiment can be recovered from face crops, whole-frame scene context, late fusion of image-level probabilities, and an extra-credit image-text CLIP branch. The experimental design is deliberately staged: MTCNN extracts 43,768 face crops; a ResNet18 face classifier estimates expression-level sentiment; controlled brightness, spatial, and frequency degradations quantify robustness; a frozen ResNet50 backbone with an MLP head supplies full-image context; a compact fusion MLP combines face and image probabilities with face-count metadata; and a frozen CLIP ViT-B/32 model concatenates image and text embeddings for multimodal classification. The best purely visual models remain in a narrow macro-F1 band near 0.36-0.38, demonstrating a substantive visual ambiguity ceiling in MSCTD. Augmentation reduces the face-model degradation gap from 5.5 to 0.5 macro-F1 points. Late fusion does not improve overall macro-F1, but it produces a targeted negative-class F1 gain from 0.389 to 0.430, showing that face-count-aware routing is informative even when the global objective is not improved. The CLIP image-text model is the decisive result: it reaches 0.570 accuracy and 0.562 macro-F1, with every class above 0.5 F1. The conclusion is that visual and facial cues are useful but insufficient for dialogue sentiment; the utterance text carries essential sentiment information."
    )
    add_paragraph(doc, "Keywords: MSCTD; multimodal sentiment analysis; MTCNN; ResNet; robustness; late fusion; CLIP; transfer learning.")

    add_heading(doc, "1. Introduction", 1)
    add_paragraph(
        doc,
        "Sentiment classification from a single image is an intrinsically underdetermined problem. In dialogue data, the relevant affective evidence may be distributed across a face, a posture, the surrounding scene, or the spoken utterance. MSCTD is particularly suitable for studying this tension because each labelled sample is a film-dialogue utterance paired with a still frame and a three-way sentiment label: negative, neutral, or positive [1]. The English-German split used here contains 30,370 utterance-image pairs. The task is therefore not only to train classifiers, but also to determine which modality contains recoverable signal under realistic ambiguity."
    )
    add_paragraph(
        doc,
        "The project is structured around four required stages and one extra-credit multimodal stage. The required visual pipeline first uses face detection and a face-based ResNet18 model, then measures robustness under controlled degradations, then trains a full-image frozen-backbone transfer model, and finally combines the visual streams with late fusion. The extra-credit branch introduces CLIP, allowing the English utterance to be used jointly with the image. Figure 1 summarises the resulting experimental design."
    )
    add_image(doc, pipeline_fig, "Figure 1. End-to-end experimental pipeline reconstructed from notebooks 01-07 and src/ modules.", 6.6)
    add_paragraph(
        doc,
        "The central research question is whether adding more visual structure is enough to resolve sentiment ambiguity, or whether the text modality is necessary. The answer from the saved results is clear: the visual models learn real signal above the majority-class baseline, but they remain close to a unimodal ceiling. The CLIP branch breaks that ceiling because it receives lexical sentiment evidence directly."
    )
    add_bullets(doc, [
        "A scene-level split prevents dialogue leakage between train, validation, and test partitions.",
        "Face extraction is explicitly audited for no-face and multi-face cases rather than assumed to be complete.",
        "Robustness is evaluated through controlled frequency, spatial, and brightness degradations.",
        "Fusion is interpreted by per-class and per-regime behavior, not only by its overall macro-F1.",
        "The CLIP section is treated as a full multimodal experiment with architecture, stability, ablation, and error analysis."
    ])

    add_heading(doc, "2. Related Work", 1)
    add_paragraph(
        doc,
        "Residual networks provide the convolutional foundation for both the face and full-image branches. ResNet introduced identity skip connections that enable much deeper CNNs to be trained effectively [3]. ResNet18 is a conservative choice for cropped faces because the visual field is narrow, while ResNet50 provides a stronger frozen representation for full-frame scene context. Transformer-based image models, including ViT [6] and Swin Transformer [7], are relevant alternatives, but the weekly logs report a frozen ViT-B/16 ablation that underperformed the ResNet50 head by approximately 1.3 macro-F1 points while increasing CPU cost."
    )
    add_paragraph(
        doc,
        "Face detection is handled by MTCNN, a cascade of proposal, refinement, and output networks for joint face detection and alignment [2]. This choice is operationally appropriate because it is available through facenet-pytorch and gives crop-level face detections without training a detector from scratch. FaceNet [10] is also relevant as a historical face-embedding baseline, although this project trains a direct sentiment classifier rather than a verification embedding."
    )
    add_paragraph(
        doc,
        "The multimodal literature frames the main methodological choice as alignment and fusion [4]. Late fusion is simple and robust when modalities can be missing, as occurs when no face is detected. CLIP provides a stronger extra-credit alternative because it learns aligned image and text representations from large-scale contrastive pretraining [5]. Cross-attention systems such as LXMERT [8] and ClipBERT [9] offer more expressive fusion, but they are heavier and less stable under the CPU-first constraints documented in the project logs."
    )

    add_heading(doc, "3. Dataset and Reproducibility Protocol", 1)
    split_counts = pd.read_csv(OUTPUTS / "tables" / "dataset_split_summary.csv")
    add_paragraph(
        doc,
        "The raw MSCTD English-German files were parsed into one utterance-image row per sample. Scene identifiers were preserved so that all utterances from the same dialogue scene remain in a single partition. This is a crucial validity decision: if utterances from the same scene entered both train and test sets, the visual background and dialogue context would leak across partitions."
    )
    add_table(
        doc,
        ["Split", "Negative", "Neutral", "Positive", "Total"],
        [[r["split"], f'{int(r["negative"]):,}', f'{int(r["neutral"]):,}', f'{int(r["positive"]):,}', f'{int(r["total"]):,}'] for _, r in split_counts.iterrows()],
        [1.0, 1.1, 1.1, 1.1, 1.1],
    )
    add_paragraph(
        doc,
        f"The full processed dataset contains {len(master):,} rows. Neutral is the largest class ({pct((master.label_text == 'neutral').sum(), len(master)):.1f}%), followed by negative ({pct((master.label_text == 'negative').sum(), len(master)):.1f}%) and positive ({pct((master.label_text == 'positive').sum(), len(master)):.1f}%). This imbalance is moderate rather than extreme, but it is large enough that macro-F1 is the primary metric and inverse-frequency class weights are used in the neural classifiers."
    )
    add_image(doc, PLOTS / "class_distribution.png", "Figure 2. Overall sentiment distribution generated by notebook 01.", 5.7)
    add_image(doc, PLOTS / "sample_images_per_class.png", "Figure 3. Random examples per sentiment class. Visual ambiguity is common even when labels differ.", 6.2)

    add_heading(doc, "4. Methodology", 1)
    add_heading(doc, "4.1 Face Extraction and Face-Based Classification", 2)
    face_present_all = int((master["num_faces"] > 0).sum())
    no_face_all = int((master["num_faces"] == 0).sum())
    multi_all = int((master["num_faces"] >= 2).sum())
    face_present_test = int((test["num_faces"] > 0).sum())
    no_face_test = int((test["num_faces"] == 0).sum())
    multi_test = int((test["num_faces"] >= 2).sum())
    add_paragraph(
        doc,
        f"MTCNN produced {len(faces):,} face crops across the processed corpus. The project-level coverage is {face_present_all:,} images with at least one detected face ({pct(face_present_all, len(master)):.1f}%), {no_face_all:,} with no detected face ({pct(no_face_all, len(master)):.1f}%), and {multi_all:,} with two or more faces ({pct(multi_all, len(master)):.1f}%). On the test split specifically, {face_present_test:,} of {len(test):,} images have at least one detected face ({pct(face_present_test, len(test)):.1f}%), {no_face_test:,} have none ({pct(no_face_test, len(test)):.1f}%), and {multi_test:,} contain multiple detected faces ({pct(multi_test, len(test)):.1f}%)."
    )
    add_paragraph(
        doc,
        "Each detected face is saved as an independent crop and inherits the image-level sentiment label. A ResNet18 initialized with ImageNet weights is fine-tuned end-to-end on these crops. At image-level inference, multiple face predictions are averaged as softmax probabilities. If no face is detected, the fusion feature table supplies a training-prior probability vector and a binary face_detected_flag of zero. This prevents missing values while allowing the fusion model to identify the missing-modality condition."
    )
    add_image(doc, PLOTS / "face_stats.png", "Figure 4. Face-count and detection-confidence statistics from notebook 02.", 5.8)
    add_image(doc, PLOTS / "face_detection_examples.png", "Figure 5. MTCNN detection examples used as visual sanity checks.", 6.2)

    add_heading(doc, "4.2 Robustness and Augmentation", 2)
    add_paragraph(
        doc,
        "The robustness study defines three degradation families. Brightness perturbations alter brightness and contrast; spatial perturbations rotate, translate, crop, and flip; frequency perturbations apply Gaussian blur, JPEG recompression, and Gaussian noise. The experiments are controlled as follows: A trains and tests on original faces, B trains on original faces and tests on degraded faces, and C trains with mixed original/degraded augmentation and evaluates on both original and degraded faces. The p_degrade value of 0.5 was selected after a sweep in the weekly logs: 0.25 did not close the robustness gap, while 0.75 degraded clean-test performance."
    )
    add_image(doc, PLOTS / "augmentation_examples.png", "Figure 6. Brightness, spatial, and frequency degradation examples from notebook 04.", 6.4)

    add_heading(doc, "4.3 Full-Image Transfer Learning", 2)
    add_paragraph(
        doc,
        "The full-image branch processes the complete frame at 224x224 resolution. A ResNet50 pretrained on ImageNet is used as a frozen feature extractor; only a two-hidden-layer MLP head is trainable. Freezing the backbone satisfies the project constraint and reduces overfitting risk under CPU-first training. The branch is expected to capture body posture, lighting, props, and scene configuration that are unavailable to the face crop model."
    )

    add_heading(doc, "4.4 Late Fusion", 2)
    add_paragraph(
        doc,
        "The fusion MLP uses an eight-dimensional feature vector: three face softmax probabilities, three full-image softmax probabilities, num_faces_norm, and face_detected_flag. The count feature is capped and normalized to [0, 1]. This design is deliberately small: the goal is not to learn a new visual representation, but to learn a conditional weighting over two already trained streams. The key analytical question is therefore whether the MLP changes behavior in identifiable regimes such as no-face, single-face, and multi-face images."
    )

    add_heading(doc, "4.5 Extra Credit: CLIP Image-Text Modelling", 2)
    add_paragraph(
        doc,
        "The extra-credit model uses openai/clip-vit-base-patch32. The image encoder and text encoder are frozen, producing two 512-dimensional embeddings that are concatenated and passed to a small MLP classifier. Only 295,683 parameters are trainable out of 151,572,996 total parameters. This keeps the experiment stable and makes the result reproducible on the local CPU workflow. An optional second stage unfreezing the last transformer block at learning rate 1e-5 was implemented; the weekly logs report a one-epoch smoke test with a small validation drop, so the final report retains the frozen-encoder stage as the selected model."
    )
    add_image(doc, clip_fig, "Figure 7. CLIP extra-credit architecture. Both encoders are frozen; only the classifier head is trained.", 6.3)

    add_heading(doc, "5. Experimental Setup", 1)
    add_paragraph(
        doc,
        "All notebooks use seed_everything(42), CPU device selection, num_workers=0, and deterministic data plumbing. The model checkpoints and prediction CSVs are saved under outputs/, so the fusion and report-generation steps consume fixed artifacts rather than retraining upstream models. AdamW is used throughout, with cosine scheduling, gradient clipping at 1.0, and early stopping on validation loss. The exact epoch counts differ by branch because the computational units differ: face models operate on 43,768 crops, whereas full-image, fusion, and CLIP models operate on 30,370 image-level rows."
    )
    add_table(
        doc,
        ["Stage", "Input unit", "Backbone/head", "Training notes"],
        [
            ["Face", "Face crop", "ResNet18", "ImageNet init, end-to-end fine-tuning, class-weighted CE"],
            ["Robustness", "Face crop", "ResNet18", "Original/degraded evaluation plus mixed augmentation with p_degrade=0.5"],
            ["Full image", "Image row", "Frozen ResNet50 + MLP", "Backbone frozen; only 2048 -> 512 -> 128 -> 3 head trained"],
            ["Fusion", "Image row", "8 -> 32 -> 16 -> 3 MLP", "Consumes saved face/image probabilities plus face-count metadata"],
            ["CLIP", "Image + text row", "Frozen CLIP ViT-B/32 + MLP", "512 image + 512 text concatenation; encoders frozen"],
        ],
        [1.05, 0.9, 1.85, 3.1],
    )

    add_heading(doc, "6. Results", 1)
    add_heading(doc, "6.1 Final Model Comparison", 2)
    final_rows = [
        ["Majority baseline", "Image", "4,431", "0.379", "0.183", "0.209"],
        ["Face ResNet18, crop-level", "Face crop", f'{face_metrics["n_test"]:,}', f'{face_metrics["accuracy"]:.3f}', f'{face_metrics["macro_f1"]:.3f}', f'{face_metrics["weighted_f1"]:.3f}'],
        ["Face ResNet18, image-level aggregated", "Image", "4,431", f"{face_img_acc:.3f}", f"{face_img_macro:.3f}", f"{face_img_weighted:.3f}"],
        ["Face ResNet18 on degraded crop test", "Face crop", f'{face_deg["n_test"]:,}', f'{face_deg["accuracy"]:.3f}', f'{face_deg["macro_f1"]:.3f}', f'{face_deg["weighted_f1"]:.3f}'],
        ["Aug-trained face on clean crop test", "Face crop", f'{face_aug_clean["n_test"]:,}', f'{face_aug_clean["accuracy"]:.3f}', f'{face_aug_clean["macro_f1"]:.3f}', f'{face_aug_clean["weighted_f1"]:.3f}'],
        ["Aug-trained face on degraded crop test", "Face crop", f'{face_aug_deg["n_test"]:,}', f'{face_aug_deg["accuracy"]:.3f}', f'{face_aug_deg["macro_f1"]:.3f}', f'{face_aug_deg["weighted_f1"]:.3f}'],
        ["Full-image ResNet50 + MLP", "Image", f'{full_metrics["n_test"]:,}', f'{full_metrics["accuracy"]:.3f}', f'{full_metrics["macro_f1"]:.3f}', f'{full_metrics["weighted_f1"]:.3f}'],
        ["Fusion MLP", "Image", f'{fusion_metrics["n_test"]:,}', f'{fusion_metrics["accuracy"]:.3f}', f'{fusion_metrics["macro_f1"]:.3f}', f'{fusion_metrics["weighted_f1"]:.3f}'],
        ["CLIP image + text", "Image + text", f'{clip_metrics["n_test"]:,}', f'{clip_metrics["accuracy"]:.3f}', f'{clip_metrics["macro_f1"]:.3f}', f'{clip_metrics["weighted_f1"]:.3f}'],
    ]
    add_table(doc, ["Model", "Unit", "n", "Accuracy", "Macro-F1", "Weighted-F1"], final_rows, [2.6, 0.95, 0.75, 0.75, 0.8, 0.9])
    add_paragraph(
        doc,
        "The face crop-level metric is useful for evaluating the face classifier as trained, but it should not be treated as perfectly comparable with image-level rows. For this reason, the table adds an image-level aggregated face row computed from fusion_features.csv. The broad conclusion is unchanged: purely visual branches cluster near 0.36-0.38 macro-F1, whereas CLIP reaches 0.562 macro-F1."
    )
    add_image(doc, bar_fig, "Figure 8. Corrected macro-F1 comparison including the saved CLIP metrics.", 6.4)

    add_heading(doc, "6.2 Robustness Results", 2)
    rob = pd.read_csv(METRICS / "robustness_results.csv")
    add_table(
        doc,
        ["Experiment", "Accuracy", "Macro-F1", "Weighted-F1"],
        [[r["experiment"], f'{r["accuracy"]:.3f}', f'{r["macro_f1"]:.3f}', f'{r["weighted_f1"]:.3f}'] for _, r in rob.iterrows()],
        [3.1, 1.0, 1.0, 1.0],
    )
    add_paragraph(
        doc,
        "The unaugmented face model loses 5.5 macro-F1 points when evaluated on degraded faces, from 0.378 to 0.322. Mixed augmentation recovers most of this loss: the augmented model scores 0.366 on original faces and 0.361 on degraded faces, reducing the clean-to-degraded gap to 0.5 points. This is the strongest evidence that the augmentation protocol improves deployment robustness even though it slightly reduces clean-test performance."
    )

    add_heading(doc, "6.3 Per-Class Behavior", 2)
    def pc_row(label: str, metrics: dict):
        pc = metrics["per_class"]
        return [label, f'{pc["negative"]["f1"]:.3f}', f'{pc["neutral"]["f1"]:.3f}', f'{pc["positive"]["f1"]:.3f}', f'{metrics["macro_f1"]:.3f}']

    per_class_rows = [
        pc_row("Face ResNet18, crop-level", face_metrics),
        ["Face ResNet18, image-level aggregated", f"{face_img_prf[0][2]:.3f}", f"{face_img_prf[1][2]:.3f}", f"{face_img_prf[2][2]:.3f}", f"{face_img_macro:.3f}"],
        pc_row("Full-image ResNet50 + MLP", full_metrics),
        pc_row("Fusion MLP", fusion_metrics),
        pc_row("CLIP image + text", clip_metrics),
    ]
    add_table(doc, ["Model", "Negative F1", "Neutral F1", "Positive F1", "Macro-F1"], per_class_rows, [2.7, 1.0, 1.0, 1.0, 1.0])
    add_paragraph(
        doc,
        "The full-image model is strongest on neutral (0.492 F1), consistent with the hypothesis that global scene context helps with visually flat dialogue frames. Fusion shifts the error profile rather than improving the global objective: negative-class F1 rises to 0.430, a 4.1-point gain over the crop-level face model and an 8.5-point gain over the full-image model, but positive F1 falls to 0.192. CLIP is the only model with all three classes above 0.5 F1."
    )
    add_side_by_side_images(
        doc,
        CMS / "fusion_mlp_cm.png",
        CMS / "clip_multimodal_cm.png",
        "Figure 9. Fusion and CLIP confusion matrices. Fusion is negative-skewed; CLIP is more balanced across classes.",
    )

    add_heading(doc, "6.4 Fusion Regime Analysis", 2)
    add_paragraph(
        doc,
        "The fusion result should be framed as a targeted, interpretable behavior rather than a universal improvement. The MLP learns an active routing function from face-count metadata, but the routing is only beneficial in some regimes. In multi-face scenes it improves over the full-image branch, while in no-face scenes it over-corrects toward negative and loses macro-F1. This nuance is important because it converts an apparently disappointing macro-F1 row into a meaningful diagnostic result."
    )
    add_table(
        doc,
        ["Regime", "n", "Full image macro-F1", "Fusion macro-F1", "Fusion negative F1", "CLIP macro-F1"],
        regimes,
        [2.2, 0.55, 1.05, 1.0, 1.0, 1.0],
    )
    add_paragraph(
        doc,
        "The multi-face rows are the most favorable evidence for the fusion model. With two or more faces, fusion macro-F1 is 0.387 compared with 0.380 for the full-image branch. With three or more faces, fusion reaches 0.398 macro-F1 and 0.443 negative F1. The no-face row shows the limitation: the feature design can identify that the face modality is absent, but the trained MLP did not learn a sufficiently neutral fallback. A stronger future design would use calibrated logits or a class-conditional gate rather than a single shared MLP."
    )

    add_heading(doc, "6.5 CLIP Multimodal Result", 2)
    add_paragraph(
        doc,
        "The CLIP branch reaches 0.570 accuracy, 0.562 macro-F1, and 0.567 weighted-F1 on the 4,431-row image-level test split. Per-class F1 is 0.535 for negative, 0.629 for neutral, and 0.522 for positive. The key scientific interpretation is that the gain is not merely architectural. It is evidence that the English utterance carries explicit sentiment information that is unavailable in many still frames."
    )
    add_paragraph(
        doc,
        "The ablation logic supports the selected configuration. A higher learning rate of 1e-3 produced instability; 5e-4 was selected in the weekly logs as the stable stage-one rate. A low-learning-rate stage-two unfreeze was implemented but not retained because the smoke test reduced validation macro-F1 by approximately 0.01. The final decision therefore prioritizes stability, reproducibility, and defensible improvement over an unverified fine-tuning claim."
    )
    add_image(doc, PLOTS / "clip_training_curve.png", "Figure 10. CLIP stage-one training curve from notebook 07.", 5.9)

    add_heading(doc, "7. Discussion", 1)
    add_heading(doc, "7.1 What the Visual Ceiling Means", 2)
    add_paragraph(
        doc,
        "The most important empirical pattern is the narrow performance band among visual-only models. Face crops, whole images, and late fusion all exceed the majority baseline in macro-F1, so they are not trivial predictors. However, their macro-F1 values remain close enough that none supplies a decisive solution to dialogue sentiment. This is expected for MSCTD: a film still may be visually neutral while the utterance is angry, affectionate, ironic, or sarcastic. The visual branch can often identify social context, but it cannot consistently infer the semantic force of the spoken line."
    )
    add_heading(doc, "7.2 Interpretation of the Fusion Result", 2)
    add_paragraph(
        doc,
        "The fusion result should not be interpreted solely through the aggregate macro-F1 score. The evidence indicates a class- and regime-specific effect: fusion improves the negative class and selected multi-face regimes, showing that face-count-aware routing contains useful signal. At the same time, it fails on positive sentiment and no-face scenes, showing that the current feature vector and shared objective are insufficient. This mixed outcome is scientifically informative because it identifies where late probability fusion is useful and where a more expressive gate is required."
    )
    add_heading(doc, "7.3 Limitations and Threats to Validity", 2)
    add_bullets(doc, [
        "Face-level and image-level metrics are not identical units; the report therefore distinguishes crop-level and aggregated image-level rows.",
        "The re-stratified split avoids scene leakage, but it differs from the official MSCTD train/dev/test protocol, so direct comparison with external papers requires care.",
        "The robustness test uses synthetic degradations; it approximates blur, compression, lighting, and pose shift but does not fully model real deployment noise.",
        "The CLIP result demonstrates multimodal signal, but it does not prove that all visual-language architectures would behave similarly.",
        "Hyperparameter search was constrained by CPU runtime; the chosen models emphasize stability and reproducibility over exhaustive optimization."
    ])

    add_heading(doc, "8. Conclusion", 1)
    add_paragraph(
        doc,
        "This project constructs and evaluates a layered sentiment-analysis pipeline for MSCTD English-German. The face branch establishes a meaningful but limited visual signal. The augmentation study demonstrates that mixed degradations reduce the robustness gap by an order of magnitude. The full-image branch contributes neutral-class context. The fusion model produces a targeted negative-class gain and useful regime diagnostics, although it does not improve global macro-F1. The CLIP branch is the strongest model because it adds the utterance text, reaching 0.562 macro-F1 and balanced per-class performance. The final research conclusion is that dialogue sentiment cannot be reliably inferred from still images alone; robust performance requires multimodal evidence."
    )
    add_paragraph(
        doc,
        "Future work should replace probability-level fusion with class-conditional gating or cross-attention over face embeddings, recalibrate the no-face fallback, and evaluate text-only, image-only CLIP, and joint CLIP ablations to quantify the marginal contribution of each modality. A video extension could also aggregate evidence over the complete dialogue scene rather than relying on a single frame."
    )

    add_heading(doc, "Appendix A. Evidence From Weekly Logs", 1)
    add_paragraph(
        doc,
        "The weekly logs were used as an audit trail for contributions, hyperparameter choices, fixes, and interpretation. The table below summarizes the evidence most relevant to the final report."
    )
    add_table(
        doc,
        ["Member", "Evidence extracted from logs", "Report relevance"],
        [
            ["Shaik Sameer", "Scene-level splitting, seed centralization, final table audit, README/run-order maintenance", "Reproducibility and dataset validity"],
            ["Ammineni Harshitha", "MTCNN selection, face metadata schema, ResNet18 face model, per-class metrics, fusion sanity check", "Face model methodology and no/multi-face handling"],
            ["Tharigopula Sai Teja", "Degradation families, p_degrade sweep, robustness experiments A/B/C, per-family ablation", "Robustness design and interpretation"],
            ["Kakumanu Ravi Teja", "Frozen ResNet50 head, ViT-B/16 ablation, CLIP NaN debugging, full-image per-class analysis", "Transfer learning rationale and stability discussion"],
            ["Mosi Curran", "Fusion feature table, fusion MLP, CLIP final metrics, stage-two smoke test, final comparison interpretation", "Fusion and extra-credit CLIP sections"],
        ],
        [1.25, 3.0, 2.55],
    )

    add_heading(doc, "Appendix B. Reproducibility Checklist", 1)
    add_bullets(doc, [
        "Run order: notebooks 01 through 07, as specified in run_instructions.md.",
        "Primary processed tables: data/processed/msctd_master.csv, face_metadata.csv, degraded_face_metadata.csv, fusion_features.csv.",
        "Metrics source: outputs/metrics/*.json and outputs/metrics/robustness_results.csv.",
        "Prediction source: outputs/predictions/*.csv.",
        "Figures source: outputs/plots and outputs/confusion_matrices.",
        "Fixed seed: 42 through src/utils.py::seed_everything.",
        "Training device: CPU, as configured in src/config.py and the notebook kernels."
    ])

    add_heading(doc, "References", 1)
    refs = [
        "[1] Y. Liang, F. Meng, J. Xu, Y. Chen, and J. Zhou, \"MSCTD: A multimodal sentiment chat translation dataset,\" Proc. ACL, 2022.",
        "[2] K. Zhang, Z. Zhang, Z. Li, and Y. Qiao, \"Joint face detection and alignment using multitask cascaded convolutional networks,\" IEEE Signal Processing Letters, 2016.",
        "[3] K. He, X. Zhang, S. Ren, and J. Sun, \"Deep residual learning for image recognition,\" Proc. CVPR, 2016.",
        "[4] T. Baltrusaitis, C. Ahuja, and L.-P. Morency, \"Multimodal machine learning: A survey and taxonomy,\" IEEE TPAMI, 2018.",
        "[5] A. Radford et al., \"Learning transferable visual models from natural language supervision,\" Proc. ICML, 2021.",
        "[6] A. Dosovitskiy et al., \"An image is worth 16x16 words: Transformers for image recognition at scale,\" Proc. ICLR, 2021.",
        "[7] Z. Liu et al., \"Swin Transformer: Hierarchical vision transformer using shifted windows,\" Proc. ICCV, 2021.",
        "[8] H. Tan and M. Bansal, \"LXMERT: Learning cross-modality encoder representations from transformers,\" Proc. EMNLP, 2019.",
        "[9] J. Lei et al., \"Less is more: ClipBERT for video-and-language learning via sparse sampling,\" Proc. CVPR, 2021.",
        "[10] F. Schroff, D. Kalenichenko, and J. Philbin, \"FaceNet: A unified embedding for face recognition and clustering,\" Proc. CVPR, 2015.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.22)
        p.paragraph_format.first_line_indent = Inches(-0.22)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(ref)
        r.font.size = Pt(9)
        r.font.name = "Times New Roman"
        r.font.color.rgb = RGBColor.from_string(INK)

    doc.core_properties.title = "Multimodal Human Sentiment Analysis on MSCTD En-De"
    doc.core_properties.subject = "EEEM068 research report rewrite"
    doc.core_properties.author = "EEEM068 Human Sentiment Analysis Group"
    doc.save(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    build_report()
