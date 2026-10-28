"""Build the B-part V5-07 candidate from adopted V5-06.

Only main slides 08--13 and B backup slide 29 are redrawn.  The rest of the
deck, including the adopted D revision, is preserved by PowerPoint itself.
All slide content remains editable; slide 11 receives a newly generated
18-second teaching video whose poster is the same as the static diagram.
"""
from __future__ import annotations

from pathlib import Path
import copy
import hashlib
import io
import json
import time
import zipfile
import xml.etree.ElementTree as ET

import pythoncom
import win32com.client


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SOURCE = ROOT / "outputs" / "智能体产业研发_V5_06.pptx"
OUTPUT = ROOT / "outputs" / "智能体产业研发_V5_07_候选.pptx"
B_ONLY = ROOT / "outputs" / "B部分投影_V5_07_候选.pptx"
B_PDF = ROOT / "outputs" / "B部分投影_V5_07_候选.pdf"
FULL_PDF = ROOT / "outputs" / "智能体产业研发_V5_07_候选_含答辩.pdf"
VIDEO = ROOT / "outputs" / "蒸馏机制_B07_18秒.mp4"
BUILD = ROOT / "_build" / "b_refinement_07"
QA = ROOT / "qa" / "b_refinement_07"
PNG_DIR = QA / "slides"
FRAMES = BUILD / "mechanism_frames_B07.pptx"

SLIDE_W = 960.0
SLIDE_H = 540.0
FONT = "Microsoft YaHei"


def color(value: str) -> int:
    value = value.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    return r | (g << 8) | (b << 16)


C = {
    "bg": color("FAF8F3"),
    "ink": color("1E3544"),
    "teal": color("167F78"),
    "rust": color("B65D3E"),
    "muted": color("667680"),
    "rule": color("D5D9D5"),
    "pale": color("E7EFEB"),
    "soft": color("F0E7DF"),
    "blue": color("3B6A92"),
    "gray": color("777777"),
    "tan": color("D59A68"),
    "white": color("FFFFFF"),
}


def set_fill(shape, fill: int | None) -> None:
    if fill is None:
        shape.Fill.Visible = 0
    else:
        shape.Fill.Visible = -1
        shape.Fill.Solid()
        shape.Fill.ForeColor.RGB = fill


def set_line(shape, line: int | None, weight: float = 1.0) -> None:
    if line is None:
        shape.Line.Visible = 0
    else:
        shape.Line.Visible = -1
        shape.Line.ForeColor.RGB = line
        shape.Line.Weight = weight


def textbox(slide, text, x, y, w, h, size=20, fill=C["ink"], bold=False,
            align=1, valign=1, margin=0, name=None):
    shape = slide.Shapes.AddTextbox(1, x, y, w, h)
    if name:
        shape.Name = name
    shape.TextFrame2.MarginLeft = margin
    shape.TextFrame2.MarginRight = margin
    shape.TextFrame2.MarginTop = margin
    shape.TextFrame2.MarginBottom = margin
    shape.TextFrame2.WordWrap = -1
    shape.TextFrame2.VerticalAnchor = valign
    shape.TextFrame2.TextRange.Text = text
    shape.TextFrame2.TextRange.Font.Name = FONT
    shape.TextFrame2.TextRange.Font.NameFarEast = FONT
    shape.TextFrame2.TextRange.Font.Size = size
    shape.TextFrame2.TextRange.Font.Bold = -1 if bold else 0
    shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = fill
    shape.TextFrame2.TextRange.ParagraphFormat.Alignment = align
    shape.Fill.Visible = 0
    shape.Line.Visible = 0
    return shape


def rect(slide, text, x, y, w, h, fill=C["pale"], size=18, text_color=C["ink"],
         bold=False, align=1, valign=3, margin=10, radius=False, name=None):
    shape = slide.Shapes.AddShape(5 if radius else 1, x, y, w, h)
    if name:
        shape.Name = name
    set_fill(shape, fill)
    set_line(shape, None)
    shape.TextFrame2.MarginLeft = margin
    shape.TextFrame2.MarginRight = margin
    shape.TextFrame2.MarginTop = margin
    shape.TextFrame2.MarginBottom = margin
    shape.TextFrame2.WordWrap = -1
    shape.TextFrame2.VerticalAnchor = valign
    shape.TextFrame2.TextRange.Text = text
    shape.TextFrame2.TextRange.Font.Name = FONT
    shape.TextFrame2.TextRange.Font.NameFarEast = FONT
    shape.TextFrame2.TextRange.Font.Size = size
    shape.TextFrame2.TextRange.Font.Bold = -1 if bold else 0
    shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = text_color
    shape.TextFrame2.TextRange.ParagraphFormat.Alignment = align
    return shape


def line(slide, x1, y1, x2, y2, fill=C["teal"], weight=2, arrow=True):
    shape = slide.Shapes.AddLine(x1, y1, x2, y2)
    shape.Line.ForeColor.RGB = fill
    shape.Line.Weight = weight
    if arrow:
        shape.Line.EndArrowheadStyle = 3
    return shape


def clear_slide(slide, keep_chart=False):
    for idx in range(slide.Shapes.Count, 0, -1):
        shape = slide.Shapes(idx)
        if keep_chart and bool(getattr(shape, "HasChart", 0)):
            continue
        shape.Delete()
    slide.FollowMasterBackground = 0
    slide.Background.Fill.Solid()
    slide.Background.Fill.ForeColor.RGB = C["bg"]


def base(slide, number, title, footer, title_size=34):
    clear_slide(slide)
    textbox(slide, "二  模型改进  Anthropic", 54, 22, 852, 25, 15, C["teal"], True)
    textbox(slide, title, 54, 66, 852, 71, title_size, C["ink"], True)
    rule = slide.Shapes.AddShape(1, 54, 142.5, 852, 1.5)
    set_fill(rule, C["rule"])
    set_line(rule, None)
    textbox(slide, footer, 54, 507, 806, 24, 12.5, C["muted"])
    textbox(slide, str(number), 875, 507, 32, 24, 13.5, C["muted"], align=2)


def footer(number, extra=""):
    text = "[4] Chen等, AAR, 2026"
    if extra:
        text += "；" + extra
    return text


def draw_08(slide):
    base(slide, 8, "一轮研究要交付可审查、可训练、可评测的方法", footer(8, "§3、§3.1—3.2"), 30)
    items = [
        ("01", "提出假设", "资料、文献与\n已有结果"),
        ("02", "冻结mini-paper", "训练前写明方法、\n数据与损失"),
        ("03", "提交实现", "代码与说明一致；\n通过规则检查"),
        ("04", "训练目标模型", "产出更新权重；\n约1张H200、30分钟"),
        ("05", "独立评测", "安全改善与\n能力退化"),
    ]
    x0, y, w, h, gap = 54, 171, 153, 210, 21.5
    for idx, (num, title, detail) in enumerate(items):
        x = x0 + idx * (w + gap)
        rect(slide, "", x, y, w, h, C["pale"], radius=True)
        textbox(slide, num, x + 12, y + 13, w - 24, 37, 23, C["rust"], True)
        textbox(slide, title, x + 12, y + 57, w - 24, 54, 18 if idx != 1 else 16.5, C["ink"], True)
        textbox(slide, detail, x + 12, y + 120, w - 24, 72, 14.5, C["muted"])
        if idx < 4:
            line(slide, x + w + 4, y + 102, x + w + gap - 4, y + 102, C["teal"], 1.7)
    textbox(slide, "基本规则：禁用评测数据；禁止从研究Agent或更强模型蒸馏", 54, 397, 852, 30, 16.5, C["teal"], True)
    textbox(slide, "筛选原则：安全改善不能以明显能力退化为代价", 54, 438, 852, 31, 16.5, C["rust"], True)


def draw_09(slide):
    base(slide, 9, "下一次尝试，能接着读到之前的成功与失败", footer(9, "§3、§3.1"))
    blocks = [
        ("多个研究Agent\n并行探索", "提出候选方法\n分别提交训练与评测"),
        ("共享记录持续累积", "文献综述、方法代码\n实验得分、失败经验"),
        ("新会话读取后继续研究", "读取持久记录继续尝试\nAgent权重不因此更新"),
    ]
    xs = [54, 359, 664]
    for i, ((title, detail), x) in enumerate(zip(blocks, xs)):
        rect(slide, "", x, 196, 242, 166, C["soft"] if i == 1 else C["pale"], radius=True)
        textbox(slide, title, x + 18, 217, 206, 58, 20, C["teal"] if i == 1 else C["ink"], True)
        textbox(slide, detail, x + 18, 288, 206, 54, 15, C["muted"])
        if i < 2:
            line(slide, x + 251, 278, x + 293, 278, C["teal"], 2)
    line(slide, 760, 389, 198, 389, C["rule"], 7)
    textbox(slide, "研究能接续：经验保存在外部记录里，而不是自动写回研究Agent参数", 54, 423, 852, 50, 21, C["teal"], True)


def draw_10(slide):
    base(slide, 10, "先用激活引导，构造一个更少谄媚的教师", footer(10, "App. D.4；机制教学示意"), 33)
    textbox(slide, "目标：让模型更少迎合用户的错误观点", 54, 164, 852, 29, 18, C["teal"], True)
    items = [
        ("1  原目标模型", "Qwen3.5-2B正常前向\n内部表示 h"),
        ("2  方向性干预", "作用于隐藏状态\n教学示意 h′＝h＋αv"),
        ("3  引导后的教师", "目标模型的引导版本\n更少倾向附和错误观点"),
        ("4  待解决问题", "推理时的临时变化\n怎样保留到正常推理？"),
    ]
    x0, y, w, h, gap = 54, 216, 196, 169, 22.5
    for idx, (title, detail) in enumerate(items):
        x = x0 + idx * (w + gap)
        rect(slide, "", x, y, w, h, C["soft"] if idx == 1 else C["pale"], radius=True)
        textbox(slide, title, x + 14, y + 19, w - 28, 41, 18, C["teal"] if idx < 3 else C["rust"], True)
        textbox(slide, detail, x + 14, y + 72, w - 28, 72, 15, C["ink"])
        if idx < 3:
            line(slide, x + w + 4, y + 84, x + w + gap - 4, y + 84, C["teal"], 1.8)
    textbox(slide, "教师来自Qwen目标模型的引导版本，不是Claude Opus 4.8", 54, 410, 852, 27, 16.5, C["teal"], True)
    textbox(slide, "激活引导改变内部表示，不是把某题正确答案拼进提示词", 54, 449, 852, 28, 15.5, C["muted"])


def draw_11(slide, stage=-1, frame=False):
    base(slide, 11, "再用KL蒸馏，把教师行为写进学生权重", footer(11, "App. D.4；机制教学示意"), 33)
    textbox(slide, "同一个输入", 374, 157, 212, 34, 19, C["ink"], True, align=2)
    line(slide, 480, 192, 215, 221, C["rule"], 2)
    line(slide, 480, 192, 745, 221, C["rule"], 2)
    teacher_fill = C["soft"] if stage in (-1, 0) else C["pale"]
    kl_fill = C["soft"] if stage in (-1, 1) else C["pale"]
    final_fill = C["soft"] if stage in (-1, 2) else C["pale"]
    rect(slide, "", 72, 222, 286, 99, teacher_fill, radius=True)
    textbox(slide, "教师 Teacher", 88, 236, 254, 29, 18, C["teal"], True)
    textbox(slide, "引导后的Qwen｜冻结权重\n产生分布 pT", 88, 271, 254, 39, 15, C["ink"])
    rect(slide, "", 602, 222, 286, 99, C["pale"], radius=True)
    textbox(slide, "学生 Student", 618, 236, 254, 29, 18, C["teal"], True)
    textbox(slide, "待训练Qwen｜参数可更新\n产生分布 pθ", 618, 271, 254, 39, 15, C["ink"])
    line(slide, 286, 322, 413, 348, C["teal"], 2)
    line(slide, 674, 322, 547, 348, C["teal"], 2)
    rect(slide, "KL分布约束\n让学生学习教师的输出倾向", 353, 342, 254, 66, kl_fill, 16, C["ink"], True, align=2, radius=True)
    line(slide, 480, 409, 480, 431, C["teal"], 2)
    rect(slide, "仅更新学生参数", 358, 431, 244, 39, final_fill, 17, C["teal"], True, align=2, radius=True)
    line(slide, 604, 450, 655, 450, C["teal"], 2)
    rect(slide, "移除引导｜正常推理\n独立评测", 664, 420, 224, 60, final_fill, 15, C["ink"], True, align=2, radius=True)
    textbox(slide, "参数更新发生在学生模型；教师提供训练目标", 54, 481, 515, 22, 15, C["teal"], True)
    textbox(slide, "KL方向与完整配方由具体方法定义", 582, 481, 324, 22, 13.5, C["muted"], align=3)
    if frame:
        textbox(slide, ["① 教师提供引导后的分布", "② KL把分布差异变成训练信号", "③ 更新学生后移除引导并评测"][stage], 608, 154, 298, 25, 13.5, C["rust"], True, align=3)


def draw_12(slide):
    base(slide, 12, "改善空间：先弄清百分数的分母", footer(12, "§2.2；定义与教学数值"))

    rect(slide, "", 54, 153, 852, 118, C["pale"], radius=True)
    textbox(slide, "定义", 72, 170, 74, 30, 18, C["teal"], True)
    textbox(slide, "改善空间关闭比例：训练带来的提升，占“基线到参考最优”原有差距的比例。", 150, 168, 738, 32, 16.5, C["ink"], True)
    textbox(slide, "(训练后得分 − 基线得分) ÷ (参考最优得分 − 基线得分)", 72, 213, 816, 35, 22, C["teal"], True, align=2)

    textbox(slide, "一个小例子", 54, 292, 250, 28, 18, C["ink"], True)
    items = [("基线", "50", C["ink"]), ("训练后", "70", C["teal"]), ("参考最优", "100", C["ink"])]
    for idx, (label, value, value_color) in enumerate(items):
        x = 54 + idx * 158
        rect(slide, "", x, 328, 132, 90, C["soft"] if idx == 1 else C["pale"], radius=True)
        textbox(slide, label, x + 12, 341, 108, 21, 14, C["muted"], align=2)
        textbox(slide, value, x + 12, 366, 108, 39, 29, value_color, True, align=2)
        if idx < 2:
            line(slide, x + 136, 373, x + 154, 373, C["teal"], 1.8)

    rect(slide, "", 574, 309, 332, 109, C["soft"], radius=True)
    textbox(slide, "代入定义", 594, 324, 292, 24, 15, C["rust"], True)
    textbox(slide, "(70 − 50) ÷ (100 − 50)", 594, 354, 292, 28, 18, C["ink"], True, align=2)
    textbox(slide, "= 40%", 594, 382, 292, 31, 24, C["teal"], True, align=2)

    textbox(slide, "直观理解：原本还差50分，现在补回20分，因此关闭了40%的原有改善空间。", 54, 440, 852, 25, 15.5, C["ink"], True)
    textbox(slide, "注意：40%不是训练后正确率；多个安全测试还要用几何平均数汇总。", 54, 474, 852, 24, 15, C["rust"], True)


def position_chart(chart_shape):
    chart_shape.Left, chart_shape.Top, chart_shape.Width, chart_shape.Height = 54, 198, 590, 253


def draw_13(slide):
    clear_slide(slide, keep_chart=True)
    chart_shape = next(slide.Shapes(i) for i in range(1, slide.Shapes.Count + 1) if bool(getattr(slide.Shapes(i), "HasChart", 0)))
    textbox(slide, "二  模型改进  Anthropic", 54, 22, 852, 25, 15, C["teal"], True)
    textbox(slide, "同一案例中，训练目标比增加数据自由度更关键", 54, 66, 852, 71, 31, C["ink"], True)
    rule = slide.Shapes.AddShape(1, 54, 142.5, 852, 1.5); set_fill(rule, C["rule"]); set_line(rule, None)
    textbox(slide, "Qwen3.5-2B谄媚任务｜前150个已评分方法", 54, 159, 852, 26, 16, C["muted"])
    position_chart(chart_shape)
    textbox(slide, "比较的是搜索条件", 669, 205, 237, 31, 19, C["teal"], True)
    textbox(slide, "允许的方法不同\n不是同一模型逐步加模块", 669, 246, 237, 56, 15.5, C["ink"])
    textbox(slide, "限定范围", 669, 325, 237, 31, 18, C["rust"], True)
    textbox(slide, "单个任务、单个目标模型\n每条件一次搜索运行\n未重跑held-out或Petri", 669, 363, 237, 78, 14.5, C["muted"])
    textbox(slide, "横轴：安全改善空间关闭比例（%）", 54, 463, 590, 27, 14, C["muted"])
    textbox(slide, "[4] Chen等, AAR, 2026；Fig.20；App. D.4", 54, 507, 806, 24, 12.5, C["muted"])
    textbox(slide, "13", 875, 507, 32, 24, 13.5, C["muted"], align=2)


def draw_29(slide):
    clear_slide(slide)
    textbox(slide, "答辩备份", 54, 22, 852, 25, 15, C["teal"], True)
    textbox(slide, "前150个方法比较：四种搜索条件，不是逐步加法", 54, 66, 852, 71, 31, C["ink"], True)
    rule = slide.Shapes.AddShape(1, 54, 142.5, 852, 1.5); set_fill(rule, C["rule"]); set_line(rule, None)
    items = [
        ("6.0%", "原样公共数据SFT"),
        ("2.9%", "自由构造数据SFT"),
        ("16.5%", "SFT＋KL自蒸馏"),
        ("23.3%", "不受限方法搜索"),
    ]
    for idx, (value, label) in enumerate(items):
        y = 176 + idx * 65
        textbox(slide, value, 54, y, 135, 46, 27, C["teal"] if idx < 2 else C["rust"], True)
        textbox(slide, label, 207, y + 2, 420, 43, 21, C["ink"])
    rect(slide, "共同口径\n前150个已评分方法", 660, 183, 246, 83, C["pale"], 17, C["ink"], True, align=2, radius=True)
    rect(slide, "不要混用\nKL全程峰值18.7%", 660, 286, 246, 83, C["soft"], 17, C["ink"], True, align=2, radius=True)
    textbox(slide, "每个条件只有一次搜索运行；该消融未重跑held-out或Petri。", 54, 449, 852, 30, 16, C["muted"])
    textbox(slide, "[4] Chen等, AAR, 2026；Fig.20；App. D.4", 54, 507, 806, 24, 12.5, C["muted"])
    textbox(slide, "29", 875, 507, 32, 24, 13.5, C["muted"], align=2)


def set_note(slide, text):
    try:
        for idx in range(1, slide.NotesPage.Shapes.Count + 1):
            shape = slide.NotesPage.Shapes(idx)
            if shape.Type == 14 and shape.PlaceholderFormat.Type == 2:
                shape.TextFrame.TextRange.Text = text
                return True
    except Exception:
        return False
    return False


def writable_or_fallback(path):
    """Use a clearly named fallback when a currently open PDF cannot be replaced."""
    if path.exists():
        try:
            with path.open("r+b"):
                pass
        except PermissionError:
            fallback = path.with_name(f"{path.stem}_更新{path.suffix}")
            fallback.unlink(missing_ok=True)
            return fallback
    return path


def patch_chart_package(path: Path):
    """Extend the existing native chart and its editable embedded workbook."""
    chart_ns = "http://schemas.openxmlformats.org/drawingml/2006/chart"
    sheet_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("c", chart_ns)
    ET.register_namespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
    ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
    ET.register_namespace("c16r2", "http://schemas.microsoft.com/office/drawing/2015/06/chart")

    categories = ["原样公共数据 SFT", "自由构造数据 SFT", "SFT + KL 自蒸馏", "不受限方法搜索"]
    values = ["0.06", "0.029", "0.165", "0.233"]

    def patch_chart(data: bytes) -> bytes:
        root = ET.fromstring(data)
        ns = {"c": chart_ns}
        cat_ref = root.find(".//c:ser/c:cat/c:strRef", ns)
        val_ref = root.find(".//c:ser/c:val/c:numRef", ns)
        cat_ref.find("c:f", ns).text = "'Chart Data'!$A$2:$A$5"
        val_ref.find("c:f", ns).text = "'Chart Data'!$B$2:$B$5"
        for cache, items in [(cat_ref.find("c:strCache", ns), categories), (val_ref.find("c:numCache", ns), values)]:
            cache.find("c:ptCount", ns).set("val", "4")
            for pt in list(cache.findall("c:pt", ns)):
                cache.remove(pt)
            for idx, value in enumerate(items):
                pt = ET.SubElement(cache, f"{{{chart_ns}}}pt", {"idx": str(idx)})
                ET.SubElement(pt, f"{{{chart_ns}}}v").text = value
        root.find(".//c:barChart/c:gapWidth", ns).set("val", "58")
        root.find(".//c:valAx/c:scaling/c:max", ns).set("val", "0.25")
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def patch_workbook(data: bytes) -> bytes:
        source = zipfile.ZipFile(io.BytesIO(data))
        target_bytes = io.BytesIO()
        with zipfile.ZipFile(target_bytes, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                content = source.read(item.filename)
                if item.filename == "xl/worksheets/sheet1.xml":
                    root = ET.fromstring(content)
                    dimension = root.find(f"{{{sheet_ns}}}dimension")
                    dimension.set("ref", "A1:B5")
                    sheet_data = root.find(f"{{{sheet_ns}}}sheetData")
                    for row in list(sheet_data):
                        sheet_data.remove(row)
                    rows = [("Category", "改善空间"), *zip(categories, values)]
                    for row_index, (label, value) in enumerate(rows, 1):
                        row = ET.SubElement(sheet_data, f"{{{sheet_ns}}}row", {"r": str(row_index)})
                        cell_a = ET.SubElement(row, f"{{{sheet_ns}}}c", {"r": f"A{row_index}", "t": "inlineStr"})
                        inline = ET.SubElement(cell_a, f"{{{sheet_ns}}}is")
                        ET.SubElement(inline, f"{{{sheet_ns}}}t").text = label
                        cell_b = ET.SubElement(row, f"{{{sheet_ns}}}c", {"r": f"B{row_index}"})
                        if row_index == 1:
                            cell_b.set("t", "inlineStr")
                            inline_b = ET.SubElement(cell_b, f"{{{sheet_ns}}}is")
                            ET.SubElement(inline_b, f"{{{sheet_ns}}}t").text = value
                        else:
                            ET.SubElement(cell_b, f"{{{sheet_ns}}}v").text = value
                    content = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                target.writestr(copy.copy(item), content)
        source.close()
        return target_bytes.getvalue()

    temp = path.with_suffix(".chart-patched.pptx")
    with zipfile.ZipFile(path) as source, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            content = source.read(item.filename)
            if item.filename == "ppt/charts/chart1.xml":
                content = patch_chart(content)
            elif item.filename in {
                "ppt/embeddings/chart-data-snapshot-001.xlsx",
                "ppt/embeddings/Microsoft_Excel_Worksheet.xlsx",
            }:
                content = patch_workbook(content)
            target.writestr(copy.copy(item), content)
    temp.replace(path)


def create_video(app):
    # Rebuild every time so changes to the editable teaching frames are reflected
    # in both the embedded poster frame and the exported MP4.
    if VIDEO.exists():
        VIDEO.unlink()
    frames = app.Presentations.Add()
    frames.PageSetup.SlideWidth = SLIDE_W
    frames.PageSetup.SlideHeight = SLIDE_H
    for stage in range(3):
        slide = frames.Slides.Add(stage + 1, 12)
        draw_11(slide, stage=stage, frame=True)
    frames.SaveAs(str(FRAMES), 24)
    frames.CreateVideo(str(VIDEO), False, 6, 720, 25, 85)
    started = time.monotonic()
    while time.monotonic() - started < 300:
        status = frames.CreateVideoStatus
        if status == 3 and VIDEO.exists() and VIDEO.stat().st_size > 10_000:
            break
        if status == 4:
            raise RuntimeError("PowerPoint video creation failed")
        time.sleep(1)
    else:
        raise TimeoutError("PowerPoint video creation timed out")
    frames.Close()
    FRAMES.unlink(missing_ok=True)
    try:
        BUILD.rmdir()
    except OSError:
        pass


def build():
    BUILD.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / "主讲内容.json").read_text(encoding="utf-8"))
    pythoncom.CoInitialize()
    app = None
    pres = None
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        create_video(app)
        pres = app.Presentations.Open(str(SOURCE), ReadOnly=0, Untitled=0, WithWindow=0)
        pres.SaveAs(str(OUTPUT), 24)
        draw_08(pres.Slides(8))
        draw_09(pres.Slides(9))
        draw_10(pres.Slides(10))
        draw_11(pres.Slides(11))
        draw_12(pres.Slides(12))
        draw_13(pres.Slides(13))
        draw_29(pres.Slides(29))
        media = pres.Slides(11).Shapes.AddMediaObject2(str(VIDEO), False, True, 0, 0, SLIDE_W, SLIDE_H)
        media.Name = "MechanismTeachingVideo_B07"
        media.AnimationSettings.PlaySettings.PlayOnEntry = True
        media.AnimationSettings.PlaySettings.HideWhileNotPlaying = False
        notes_ok = []
        for number in range(8, 14):
            slide_data = data[number - 1]
            note = (
                f"主讲第{number}页，设计预算{slide_data['seconds']}秒，未真人计时。\n"
                f"{slide_data['script']}\n{slide_data.get('note', '')}\n"
                "来源：[4] https://alignment.anthropic.com/2026/automated-alignment-researchers/"
            )
            notes_ok.append(set_note(pres.Slides(number), note))
        set_note(pres.Slides(29), "Fig.20四条件共同前150个方法：6.0%、2.9%、16.5%、23.3%。16.5%不要与KL完整运行峰值18.7%混用。")
        pres.Save()
        pres.Close(); pres = None

        patch_chart_package(OUTPUT)
        pres = app.Presentations.Open(str(OUTPUT), ReadOnly=0, Untitled=0, WithWindow=0)
        for number in range(8, 14):
            pres.Slides(number).Export(str(PNG_DIR / f"{number:02}.png"), "PNG", 1280, 720)
        actual_full_pdf = writable_or_fallback(FULL_PDF)
        pres.SaveCopyAs(str(actual_full_pdf), 32)
        pres.SaveCopyAs(str(B_ONLY), 24)
        pres.Close(); pres = None

        b_pres = app.Presentations.Open(str(B_ONLY), ReadOnly=0, Untitled=0, WithWindow=0)
        for number in range(b_pres.Slides.Count, 13, -1):
            b_pres.Slides(number).Delete()
        for number in range(7, 0, -1):
            b_pres.Slides(number).Delete()
        b_pres.Save()
        actual_b_pdf = writable_or_fallback(B_PDF)
        b_pres.SaveCopyAs(str(actual_b_pdf), 32)
        b_pres.Close()

        manifest = {
            "base": str(SOURCE.relative_to(REPO)).replace("\\", "/"),
            "candidate": str(OUTPUT.relative_to(REPO)).replace("\\", "/"),
            "fullPdf": str(actual_full_pdf.relative_to(REPO)).replace("\\", "/"),
            "bOnlyPptx": str(B_ONLY.relative_to(REPO)).replace("\\", "/"),
            "bOnlyPdf": str(actual_b_pdf.relative_to(REPO)).replace("\\", "/"),
            "candidateSha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
            "slidesChanged": [8, 9, 10, 11, 12, 13, 29],
            "mainBSlides": [8, 9, 10, 11, 12, 13],
            "otherMainSlidesPreserved": True,
            "designSeconds": sum(data[n - 1]["seconds"] for n in range(8, 14)),
            "video": str(VIDEO.relative_to(REPO)).replace("\\", "/"),
            "videoSha256": hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
            "videoDesignSeconds": 18,
            "notesUpdated": all(notes_ok),
            "nativeChartSlide13": True,
            "status": "candidate_pending_leader_review_and_human_timing",
        }
        (QA / "build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False))
    finally:
        if pres is not None:
            try:
                pres.Close()
            except Exception:
                pass
        if app is not None:
            try:
                if app.Presentations.Count == 0:
                    app.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    build()
