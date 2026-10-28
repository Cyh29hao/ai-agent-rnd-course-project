"""Verify the B-section V5-07 candidate without promoting it to the official version."""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import xml.etree.ElementTree as ET

import pythoncom
import win32com.client
from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "outputs"
QA = ROOT / "qa" / "b_refinement_07"
BASE_PNG = ROOT / "qa" / "powerpoint_06"
FULL_PNG = QA / "full_slides"
PPTX = OUT / "智能体产业研发_V5_07_候选.pptx"
B_ONLY = OUT / "B部分投影_V5_07_候选.pptx"
FULL_PDF = OUT / "智能体产业研发_V5_07_候选_含答辩.pdf"
B_PDF = OUT / "B部分投影_V5_07_候选.pdf"
VIDEO = OUT / "蒸馏机制_B07_18秒.mp4"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text):
    return re.sub(r"\W+", "", text)


def slide_count(package):
    with ZipFile(package) as z:
        xml = ET.fromstring(z.read("ppt/presentation.xml"))
    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    return len(xml.findall(".//p:sldId", ns))


def pdf_page_count(path):
    # PowerPoint exports one /Type /Page object per page; /Pages is excluded.
    return len(re.findall(rb"/Type\s*/Page(?!s)\b", path.read_bytes()))


def export_pngs():
    FULL_PNG.mkdir(parents=True, exist_ok=True)
    pythoncom.CoInitialize()
    app = None
    pres = None
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        pres = app.Presentations.Open(str(PPTX), ReadOnly=1, Untitled=0, WithWindow=0)
        for number in range(1, pres.Slides.Count + 1):
            pres.Slides(number).Export(str(FULL_PNG / f"{number:02}.png"), "PNG", 1280, 720)
    finally:
        if pres is not None:
            pres.Close()
        if app is not None and app.Presentations.Count == 0:
            app.Quit()
        pythoncom.CoUninitialize()


def verify():
    manifest = json.loads((QA / "build_manifest.json").read_text(encoding="utf-8"))
    full_pdf = REPO / manifest.get("fullPdf", str(FULL_PDF.relative_to(REPO)))
    b_pdf = REPO / manifest.get("bOnlyPdf", str(B_PDF.relative_to(REPO)))
    required = [PPTX, B_ONLY, full_pdf, b_pdf, VIDEO]
    assert all(path.exists() and path.stat().st_size > 10_000 for path in required)
    assert slide_count(PPTX) == 34
    assert slide_count(B_ONLY) == 6
    assert pdf_page_count(full_pdf) == 34
    assert pdf_page_count(b_pdf) == 6

    data = json.loads((ROOT / "主讲内容.json").read_text(encoding="utf-8"))
    assert sum(data[number - 1]["seconds"] for number in range(8, 14)) == 260
    spoken = (ROOT / "01_自然口播稿.md").read_text(encoding="utf-8")

    with ZipFile(PPTX) as z:
        assert "ppt/charts/chart1.xml" in z.namelist()
        chart_text = "".join(ET.fromstring(z.read("ppt/charts/chart1.xml")).itertext())
        for expected in ["原样公共数据 SFT", "自由构造数据 SFT", "SFT + KL 自蒸馏", "不受限方法搜索"]:
            assert expected in chart_text, expected
        for expected in ["0.06", "0.029", "0.165", "0.233"]:
            assert expected in chart_text, expected

        workbook_names = [
            name for name in z.namelist()
            if name.startswith("ppt/embeddings/") and name.lower().endswith(".xlsx")
        ]
        assert workbook_names
        workbook_name = workbook_names[0]
        with ZipFile(BytesIO(z.read(workbook_name))) as workbook:
            workbook_text = "".join(
                "".join(ET.fromstring(workbook.read(name)).itertext())
                for name in workbook.namelist()
                if name.startswith("xl/worksheets/") and name.endswith(".xml")
            )
            for expected in ["0.06", "0.029", "0.165", "0.233"]:
                assert expected in workbook_text, expected

        slide11_rels = z.read("ppt/slides/_rels/slide11.xml.rels").decode("utf-8")
        assert "video" in slide11_rels.lower() or ".mp4" in slide11_rels.lower()
        assert any(name.startswith("ppt/media/") and name.lower().endswith(".mp4") for name in z.namelist())
        slide13_rels = z.read("ppt/slides/_rels/slide13.xml.rels").decode("utf-8")
        assert "chart" in slide13_rels.lower()

        for number in range(8, 14):
            note = ET.fromstring(z.read(f"ppt/notesSlides/notesSlide{number}.xml"))
            note_text = "".join(note.itertext())
            script = data[number - 1]["script"]
            assert norm(script) in norm(note_text), number
            assert script in spoken, number

    export_pngs()
    changed = []
    for number in range(1, 35):
        before = Image.open(BASE_PNG / f"{number:02}.png").convert("RGB")
        after = Image.open(FULL_PNG / f"{number:02}.png").convert("RGB")
        if ImageChops.difference(before, after).getbbox():
            changed.append(number)
    assert changed == [8, 9, 10, 11, 12, 13, 29], changed

    result = {
        "status": "pass",
        "revision": "V5-07-candidate",
        "officialVersionPromoted": False,
        "mainSlides": 24,
        "totalSlides": 34,
        "BOnlySlides": 6,
        "fullPdf": str(full_pdf.relative_to(REPO)).replace("\\", "/"),
        "bOnlyPdf": str(b_pdf.relative_to(REPO)).replace("\\", "/"),
        "changedProjectionPages": changed,
        "otherProjectionPagesPixelIdenticalToV5_06": True,
        "BDesignSeconds": 260,
        "humanTimingVerified": False,
        "speakerNotesMatchSource": True,
        "slide11EmbeddedMp4": True,
        "slide13NativeEditableChart": True,
        "slide13Values": [0.06, 0.029, 0.165, 0.233],
        "candidateSha256": sha256(PPTX),
        "videoSha256": sha256(VIDEO),
    }
    (QA / "verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    verify()
