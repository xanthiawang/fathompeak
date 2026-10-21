"""Compose approved vector wordmark, ImageGen art, and editable text. Run in place."""
from pathlib import Path
import base64
import copy
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def embedded(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def wordmark(x, y, width):
    root = ET.parse(ROOT / "05_品牌标识/现用/官方logo_2026-10-18/primary.svg").getroot()
    mark = copy.deepcopy(next(g for g in root if g.get("id") == "英文科技字标"))
    mark.attrib.pop("transform", None)
    return f'<g transform="translate({x} {y}) scale({width/722})">{ET.tostring(mark, encoding="unicode")}</g>'


def peak_symbol(x, y, width=120):
    """Place the approved vector symbol with its original paths and gradients."""
    symbol = ET.parse(ROOT / "05_品牌标识/现用/官方logo_2026-10-18/symbol.svg").getroot()
    symbol.set("x", str(x))
    symbol.set("y", str(y))
    symbol.set("width", str(width))
    symbol.set("height", str(width * 260 / 680))
    return ET.tostring(symbol, encoding="unicode")


def text(x, y, value, size=36, fill="#222", family="Noto Sans SC", extra=""):
    if value in ("沐仞科技", "FATHOMPEAK"):
        import re
        filename = "wordmark-zh.svg" if value == "沐仞科技" else "wordmark-en.svg"
        mark = ET.parse(ROOT / "05_品牌标识/现用/官方logo_2026-10-18" / filename).getroot()
        _, _, w, h = map(float, mark.get("viewBox").split())
        height = size * (0.9 if value == "沐仞科技" else 0.72)
        width = w / h * height
        if 'text-anchor="end"' in extra: x -= width
        if 'text-anchor="middle"' in extra: x -= width/2
        mark.set("x", str(x)); mark.set("y", str(y-height))
        mark.set("width", str(width)); mark.set("height", str(height))
        mark.set("aria-label", value)
        for n in mark.iter():
            if n.get("fill") not in (None, "none"): n.set("fill", fill)
        return ET.tostring(mark, encoding="unicode")
    family = {"Hiragino Sans GB": "Noto Sans SC", "Songti SC": "Noto Serif SC", "Arial": "DM Sans"}.get(family, family)
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" {extra}>{value}</text>'


def canvas(height, title, art):
    return f'''<svg xmlns="{NS}" width="1800" height="{height}" viewBox="0 0 1800 {height}">
<title>{title}</title><rect width="1800" height="{height}" fill="white"/>
<image href="{embedded(HERE / "assets" / art)}" width="1800" height="{height}" preserveAspectRatio="xMidYMid slice"/>
'''


def export(name, svg):
    source = HERE / f"{name}.svg"
    source.write_text(svg + "</svg>", encoding="utf-8")
    subprocess.run(["rsvg-convert", str(source), "-o", str(HERE / f"{name}.png")], check=True)


def build():
    opening = canvas(760, "沐仞科技 · 公众号开头主视觉", "opening-art.png")
    opening += wordmark(82, 78, 292)
    opening += text(410, 100, "沐仞科技", 28)
    opening += '<line x1="82" y1="142" x2="1718" y2="142" stroke="#dedede"/>'
    opening += text(82, 315, "以绿色能源", 88, family="Songti SC")
    opening += text(82, 430, "承载全球计算。", 88, family="Songti SC")
    opening += text(86, 518, "算电协同 · 词元直供", 36, "#555")
    opening += text(86, 688, "ENERGY  /  COMPUTE  /  INTELLIGENCE", 19, "#777", "Arial", 'letter-spacing="2"')
    opening += text(1718, 688, "FATHOMPEAK", 20, "#666", "Arial", 'text-anchor="end" letter-spacing="3"')
    export("01_开头主视觉_1800x760", opening)

    ending = canvas(900, "沐仞科技 · 公众号结尾介绍卡", "ending-art.png")
    ending += text(88, 90, "ABOUT FATHOMPEAK", 20, "#666", "Arial", 'letter-spacing="3"')
    ending += '<line x1="388" y1="82" x2="1712" y2="82" stroke="#d9d9d9"/>'
    ending += wordmark(88, 184, 920)
    ending += text(88, 356, "沐仞科技", 76, family="Songti SC")
    ending += text(90, 442, "以绿色能源承载全球计算。", 44)
    ending += '<line x1="90" y1="492" x2="148" y2="492" stroke="#222" stroke-width="3"/>'
    ending += text(90, 562, "连接新能源电站与 AI 计算需求，", 38, "#555")
    ending += text(90, 622, "用算电协同，组织从绿电到词元的供给。", 38, "#555")
    ending += text(90, 735, "模型 API  /  词元工厂  /  算电协同", 32)
    ending += text(90, 831, "栉风沐雨，登高万仞。", 28, "#777", "Songti SC")
    ending += '<rect x="1330" y="442" width="390" height="390" rx="18" fill="white" stroke="#e4e4e4"/>'
    ending += f'<image href="{embedded(HERE / "assets/wechat-qr.png")}" x="1375" y="462" width="300" height="300"/>'
    ending += text(1525, 800, "扫码关注沐仞科技", 28, "#222", extra='text-anchor="middle"')
    export("02_结尾介绍卡_1800x900", ending)


if __name__ == "__main__":
    try:
        if not any(flag in sys.argv for flag in ("--every", "--article")):
            build()
    except (OSError, subprocess.CalledProcessError, StopIteration) as error:
        raise SystemExit(f"Card build failed: {error}") from error


def build_every():
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen

    output = HERE / ("article-compute-energy" if "--article" in sys.argv else "every-v2")
    fonts = output / "assets/fonts"
    if "--article" in sys.argv:
        from build_architecture_20261020 import article_source
        from fontTools.varLib.instancer import instantiateVariableFont
        from fontTools import subset
        required = set(article_source().read_text() + "相关资源获取模型与服务接入指南电站合作更多信息官方网址微信咨询扫码关注下方沐仞科技公众号商务合作主视觉与正文插图")
        for stem, full in [
            ("Noto-sans-SC", "/tmp/fathompeak-article-noto-sans-full.ttf"),
            ("Noto-serif-SC", "/tmp/fathompeak-article-noto-serif-full.ttf"),
        ]:
            existing = TTFont(fonts / (stem + ".ttf"))
            points = set(existing.getBestCmap())
            missing = {ord(c) for c in required if ord(c) > 127} - points
            if missing:
                fullfont = TTFont(full)
                if "fvar" in fullfont:
                    fullfont = instantiateVariableFont(fullfont, {"wght": 400}, inplace=True)
                sub = subset.Subsetter()
                sub.populate(unicodes=points | {ord(c) for c in required})
                sub.subset(fullfont)
                fullfont.save(fonts / (stem + ".ttf"))
        # Real semibold glyphs instead of synthesized bold on the regular subset.
        semibold = instantiateVariableFont(
            TTFont("/tmp/fathompeak-article-noto-sans-full.ttf"),
            {"wght": 600}, inplace=True
        )
        sub = subset.Subsetter()
        sub.populate(text="".join(sorted(required)))
        sub.subset(semibold)
        semibold.save(fonts / "Noto-sans-SC-Semibold.ttf")
        if "--copy-only" in sys.argv:
            update_article_copy(output)
            return
    config = Path("/tmp/fathompeak-editorial-fonts.conf")
    config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>{fonts}</dir><cachedir>/tmp/fathompeak-fontcache</cachedir></fontconfig>')
    env = dict(os.environ, FONTCONFIG_FILE=str(config))
    families = {"Fraunces": "Fraunces", "DM Sans": "DM-Sans", "DM Mono": "DM-Mono", "Pinyon Script": "Pinyon-Script", "Noto Serif SC": "Noto-serif-SC", "Noto Sans SC": "Noto-sans-SC"}
    faces = "".join(f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{base64.b64encode((fonts / (file + '.ttf')).read_bytes()).decode()}) format('truetype');font-weight:400;}}" for family, file in families.items())
    loaded = {}
    for family, filename in families.items():
        font_path = fonts / f"{filename}.ttf"
        tt = TTFont(font_path)
        hb_font = hb.Font(hb.Face(font_path.read_bytes()))
        loaded[family] = (tt, hb_font, tt.getBestCmap())

    def render_precise(source):
        """Shape text with the actual brand font bytes; keep editable original."""
        document = ET.parse(source)
        tree = document.getroot()
        for parent in list(tree.iter()):
            for node in list(parent):
                if node.tag != f"{{{NS}}}text":
                    continue
                value = "".join(node.itertext())
                preferred = node.get("font-family", "DM Sans")
                runs = []
                for char in value:
                    selected = preferred if preferred in loaded and ord(char) in loaded[preferred][2] else next((name for name in ("DM Sans", "Noto Sans SC") if ord(char) in loaded[name][2]), None)
                    if selected is None:
                        raise ValueError(f"Missing brand font glyph: {char!r}")
                    if runs and runs[-1][0] == selected:
                        runs[-1][1] += char
                    else:
                        runs.append([selected, char])
                x = float(node.get("x", 0))
                y = float(node.get("y", 0))
                size = float(node.get("font-size", 36))
                spacing = float(node.get("letter-spacing", 0))
                group = ET.Element(f"{{{NS}}}g", {"fill": node.get("fill", "#222"), "aria-label": value})
                cursor = 0
                for family, run in runs:
                    tt, hb_font, _ = loaded[family]
                    scale = size / tt["head"].unitsPerEm
                    buffer = hb.Buffer()
                    buffer.add_str(run)
                    buffer.guess_segment_properties()
                    hb.shape(hb_font, buffer)
                    glyphs = tt.getGlyphSet()
                    order = tt.getGlyphOrder()
                    for info, position in zip(buffer.glyph_infos, buffer.glyph_positions):
                        pen = SVGPathPen(glyphs)
                        glyphs[order[info.codepoint]].draw(pen)
                        path = pen.getCommands()
                        if path:
                            ET.SubElement(group, f"{{{NS}}}path", {
                                "d": path,
                                "transform": f"translate({cursor + position.x_offset * scale} {-position.y_offset * scale}) scale({scale} {-scale})",
                            })
                        cursor += position.x_advance * scale + spacing
                anchor = node.get("text-anchor")
                x -= cursor if anchor == "end" else cursor / 2 if anchor == "middle" else 0
                group.set("transform", f"translate({x} {y})")
                index = list(parent).index(node)
                parent.remove(node)
                parent.insert(index, group)
        outlined = source.with_name(source.stem + "_outlined.svg")
        document.write(outlined, encoding="unicode", xml_declaration=True)
        subprocess.run(["rsvg-convert", str(outlined), "-o", str(source.with_suffix(".png"))], env=env, check=True)

    def start(height):
        return f'<svg xmlns="{NS}" width="1800" height="{height}" viewBox="0 0 1800 {height}"><style>{faces}</style><rect width="1800" height="{height}" fill="white"/>'

    def img(path, x=0, y=0, width=1800, height=760, opacity=1, fit="xMidYMid slice"):
        return f'<image href="{embedded(path)}" x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" preserveAspectRatio="{fit}"/>'

    def save(name, content, height):
        svg = output / f"{name}.svg"
        svg.write_text(content + "</svg>")
        render_precise(svg)

    if "--article" in sys.argv:
        build_article(output, start, img, save)
        return

    # Correct the first silver direction with the same real brand fonts.
    for name in ("01_开头主视觉_1800x760", "02_结尾介绍卡_1800x900"):
        source = (HERE / (name + ".svg")).read_text()
        source = source.replace('font-family="Songti SC"', 'font-family="Noto Serif SC"').replace('font-family="Hiragino Sans GB"', 'font-family="Noto Sans SC"').replace('font-family="Arial"', 'font-family="DM Sans"')
        source = source.replace("<title>", "<style>" + faces + "</style><title>", 1)
        target = output / ("00_" + name + "_品牌字体.svg")
        target.write_text(source)
        render_precise(target)

    names = {"A": "黑白版画", "B": "晨蓝拼贴", "C": "暮紫线稿"}
    accents = {"A": "#212021", "B": "#2F63B8", "C": "#3D314F"}
    for key, label in names.items():
        art = output / f"assets/{key}-art.png"
        accent = accents[key]
        opening = start(760)
        opening += img(art, y=112 if key == "A" else 0)
        opening += peak_symbol(80, 52) + wordmark(220, 66, 258) + text(509, 87, "沐仞科技", 26)
        opening += '<line x1="80" y1="126" x2="850" y2="126" stroke="#dedede"/>'
        if key == "A":
            opening += text(82, 250, "Energy into", 104, "#111", "Fraunces")
            opening += text(82, 370, "intelligence.", 104, "#111", "Fraunces")
            opening += text(88, 438, "以绿色能源，承载全球计算。", 36, "#333", "Noto Serif SC")
        else:
            # Single Latin initial is the approved Pinyon Script accent.
            opening += text(78, 293, "E", 125, accent, "Pinyon Script") if key == "B" else text(82, 293, "E", 100, "#111", "Fraunces")
            opening += text(150 if key == "B" else 145, 293, "nergy into", 100, "#111", "Fraunces")
            opening += text(82, 406, "intelligence.", 100, "#111", "Fraunces")
            opening += text(88, 488, "以绿色能源，承载全球计算。", 36, "#333", "Noto Serif SC")
            opening += text(88, 568, "算电协同 · 词元直供", 28, accent)
            opening += text(88, 687, "FROM ENERGY TO INTELLIGENCE", 18, "#555", "DM Mono")
        save(f"{key}_开头_{label}", opening, 760)

        ending = start(900)
        ending += img(art, y=180 if key == "A" else 0, opacity=.24 if key == "A" else .75, height=900)
        ending += '<rect x="60" y="148" width="1080" height="700" fill="white" opacity=".96"/>'
        ending += peak_symbol(82, 52) + wordmark(222, 66, 320) + text(580, 91, "沐仞科技", 30)
        ending += '<line x1="82" y1="130" x2="850" y2="130" stroke="#dedede"/>'
        ending += text(82, 270, "Built on", 90, "#111", "Fraunces")
        ending += text(82, 378, "better energy.", 90, "#111", "Fraunces")
        ending += text(88, 471, "以绿色能源承载全球计算。", 42, accent, "Noto Serif SC")
        ending += text(88, 565, "连接新能源电站与 AI 计算需求，", 34, "#444")
        ending += text(88, 621, "用算电协同，组织从绿电到词元的供给。", 34, "#444")
        ending += text(88, 742, "模型 API  /  词元工厂  /  算电协同", 28, "#333")
        ending += text(88, 829, "栉风沐雨，登高万仞。", 25, "#555", "Noto Serif SC")
        ending += '<rect x="1328" y="442" width="392" height="392" rx="8" fill="white" stroke="#d8d8d8"/>'
        ending += img(HERE / "assets/wechat-qr.png", 1374, 462, 300, 300)
        ending += text(1524, 800, "扫码关注沐仞科技", 26, "#222", extra='text-anchor="middle"')
        save(f"{key}_结尾_{label}", ending, 900)

    # A standalone article illustration sits below the recurring masthead.
    hero_art = output / "assets/article-key-visual-20261020.png"
    if hero_art.exists():
        hero = start(1200)
        hero += img(hero_art, width=1800, height=1200)
        hero += peak_symbol(80, 52) + wordmark(220, 66, 258) + text(509, 87, "沐仞科技", 26)
        hero += text(86, 254, "从绿电，", 98, "#111", "Noto Serif SC")
        hero += text(86, 380, "到智能。", 98, "#111", "Noto Serif SC")
        hero += text(92, 442, "FROM GREEN POWER TO INTELLIGENCE", 22, "#2F63B8", "DM Mono")
        save("D_独立文章主视觉_从绿电到智能_1800x1200", hero, 1200)

    board = f'<svg xmlns="{NS}" width="1800" height="1670" viewBox="0 0 1800 1670"><style>{faces}</style><rect width="1800" height="1670" fill="#f5f5f5"/>'
    board += text(60, 82, "FathomPeak / Editorial directions", 46, "#111", "Fraunces")
    board += text(60, 135, "A / B / C", 22, "#444", "DM Mono")
    board += text(620, 135, "OPENING", 18, "#555", "DM Mono")
    board += text(1440, 135, "CLOSING", 18, "#555", "DM Mono")
    for i, (key, label) in enumerate(names.items()):
        y = 184 + i * 488
        board += text(60, y + 30, f"{key}  {label}", 32, accents[key], "Noto Serif SC")
        board += img(output / f"{key}_开头_{label}.png", 60, y + 62, 900, 380)
        board += img(output / f"{key}_结尾_{label}.png", 1000, y + 62, 740, 370)
    target = output / "00_三方向对比.svg"
    target.write_text(board + "</svg>")
    render_precise(target)


def update_article_copy(output):
    """Replace live article text while retaining every approved visual asset."""
    from lxml import html as lh
    import json
    import hashlib
    from build_architecture_20261020 import article_source, integrate_article, select_editorial
    source = article_source()
    blocks = source.read_text().strip().split("\n\n")
    root = lh.fromstring((output / "index.html").read_text())
    article = root.xpath("//article")[0]
    for node in list(article):
        if node.get("data-source") or node.tag == "figure":
            article.remove(node)
    title = lh.Element("h1", {"data-source": "title"})
    title.text = blocks[0].removeprefix("# ")
    article.insert(0, title)
    closing = article.xpath('./img[@src="assets/closing.png"]')[0]
    for block in blocks[1:]:
        heading = block.startswith("## ")
        node = lh.Element("h2" if heading else "p", {"data-source": "heading" if heading else "paragraph"})
        node.text = block[3:] if heading else block
        closing.addprevious(node)
    assert [n.text_content() for n in root.xpath('//*[@data-source]')] == [
        b.removeprefix("# ").removeprefix("## ") for b in blocks
    ]
    (output / "index.html").write_text("<!doctype html>\n" + lh.tostring(root, encoding="unicode", method="html"))
    manifest = json.loads((output / "配图清单.json").read_text())
    manifest["original_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest["source_file"] = source.name
    (output / "配图清单.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    select_editorial()
    integrate_article()
    print(f"Updated article copy from {source.name}; preserved approved images.")


def build_article(output, start, img, save):
    """Typeset the supplied article without rewriting it; insert six anchored figures."""
    import html
    import json
    import hashlib
    import shutil

    for source, target in [("B_开头_晨蓝拼贴.png", "masthead.png"), ("B_结尾_晨蓝拼贴.png", "closing.png")]:
        shutil.copy2(HERE / "every-v2" / source, output / "assets" / target)

    blue = "#2F63B8"
    figures = []
    def center(x, y, value, size=48, color="#222", family="Noto Sans SC"):
        return text(x, y, html.escape(value), size, color, family, 'text-anchor="middle"')
    def arrow(path):
        return f'<path d="{path}" fill="none" stroke="{blue}" stroke-width="3" marker-end="url(#arrow)"/>'
    def base(index, title, height=1000):
        s = start(height)
        s += f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="{blue}"/></marker></defs>'
        s += text(80, 64, f"FATHOMPEAK / FIG. {index:02}", 26, blue, "DM Mono")
        s += text(80, 145, title, 56, "#111", "Noto Serif SC")
        return s
    def finish(index, title, anchor, caption, s, height=1000):
        filename = f"{index:02}_{title}"
        save(filename, s, height)
        figures.append({"index": index, "title": title, "file": filename, "after_paragraph_start": anchor, "caption": caption})

    # Independent story cover; the complete article title remains live text above.
    hero_art = output / "architecture-editorial-v3/assets/00-hero.png"
    if not hero_art.exists(): hero_art = output / "assets/00-art.png"
    cover = start(1200) + img(hero_art, height=1200)
    save("00_文章主视觉_从绿电到词元供给", cover, 1200)

    s = base(1, "一次模型服务交付，背后是三类约束")
    s += img(output / "assets/01-art.png", 80, 195, 1640, 470)
    for x, title, desc in [(350,"供电条件","发电量与电价"),(900,"计算资源","设备负载与能耗"),(1450,"通信约束","网络延迟与传输")]:
        s += center(x, 740, title, 58) + center(x, 810, desc, 42, "#555")
    s += '<path d="M350 855 V885 H1450 V855 M900 885 V905" fill="none" stroke="#2F63B8" stroke-width="3"/>'
    s += center(900, 960, "共同影响任务的执行与交付", 44, blue)
    finish(1, "一次交付的三类约束", "但真实计算任务往往同时受到这些条件约束。",
           "图 1｜电力、设备与网络共同影响模型服务交付。关系示意，不表示性能测量结果。", s)

    s = base(2, "前店后厂：把电站侧计算组织成模型服务")
    s += img(output / "assets/02-art.png", 80, 190, 1640, 475)
    for x, title, desc in [(350,"能源侧","电站提供可用能源"),(900,"后厂 · 词元工厂","电站侧设备执行任务"),(1450,"前店 · 交易平台","开发者与企业采购服务")]:
        s += center(x, 735, title, 47) + center(x, 805, desc, 38, "#555")
    s += arrow("M540 870 H700") + arrow("M1090 870 H1250")
    s += center(900, 960, "统一考虑设备、能源与网络条件", 43, blue)
    finish(2, "前店后厂的供给关系", "围绕这一方向，我们推进算电协同的“前店后厂”方案，",
           "图 2｜“后厂”组织电站侧词元生产，“前店”提供模型服务采购入口。业务关系示意。", s)

    s = base(3, "统一调度：让资源条件进入任务安排", 1160)
    # The illustration anchors the concept; typed nodes and arrows carry exact meaning.
    inputs = [(280,"设备负载"),(690,"GPU 能耗"),(1100,"发电量与电价"),(1510,"网络延迟")]
    for x, label in inputs:
        s += f'<rect x="{x-180}" y="225" width="360" height="110" rx="8" fill="#fff" stroke="#b8c7dc" stroke-width="2"/>'
        s += center(x, 295, label, 43)
        s += f'<path d="M{x} 335 V395 H900" fill="none" stroke="{blue}" stroke-width="3"/>'
    s += img(output / "assets/03-art.png", 480, 420, 840, 380)
    s += arrow("M900 395 V440")
    s += center(900, 820, "协同调度", 64)
    s += center(900, 890, "算力集群管理  /  电力资源管理", 42, "#555")
    s += arrow("M900 920 V967")
    s += '<rect x="410" y="988" width="980" height="110" rx="8" fill="#edf3fb"/>'
    s += center(900, 1058, "结合业务约束，分配与执行任务", 48, blue)
    finish(3, "统一调度的输入与任务安排", "这不只是工程技巧，更是实现算电协同的前提：",
           "图 3｜文中所述调度条件与任务安排关系。概念示意，不是完整软件部署架构。", s, 1160)

    s = base(4, "两类工程问题：计算映射与网络约束")
    s += img(output / "assets/04-art.png", 80, 190, 1640, 475)
    s += '<line x1="900" y1="680" x2="900" y2="925" stroke="#d6d6d6" stroke-width="2"/>'
    for x, name, line1, line2 in [
        (470,"Tapestrix","模型与设备之间的映射","多卡、多机与异构设备"),
        (1330,"NetWeaver","把网络延迟纳入任务安排","协同考虑传输、存储与计算"),
    ]:
        s += center(x, 745, name, 65, "#111", "Fraunces")
        s += center(x, 825, line1, 42) + center(x, 895, line2, 38, "#555")
    finish(4, "Tapestrix与NetWeaver的分工", "在计算侧，Tapestrix 首先处理模型与设备之间的映射。",
           "图 4｜按原文概括 Tapestrix 与 NetWeaver 处理的不同问题；并列介绍不表示二者的具体调用拓扑。", s)

    s = base(5, "设备进入现场，部署形态随条件选择")
    s += img(output / "assets/05-art.png", 80, 185, 1640, 495)
    for x, label in [(330,"风冷一体机"),(780,"塔式液冷一体机"),(1390,"可移动集装箱")]:
        s += center(x, 770, label, 49)
    s += center(900, 880, "电站条件  /  散热条件  /  网络条件  /  运维要求", 40, "#555")
    s += center(900, 955, "产品形态示意 · 非实物照片或工程图", 34, blue)
    finish(5, "三类现场部署形态", "设备部署则更接近电站现场。",
           "图 5｜正文提及的三类部署形态。插画不代表已定型设备外观、实物照片或已完成的项目。", s)

    s = base(6, "从单点设备，到持续调整的服务供给", 1100)
    s += img(output / "assets/06-art.png", 80, 200, 1640, 450)
    for x, label, sub in [(285,"电站供能","能源条件"),(695,"设备执行","任务运行"),(1105,"平台交易","模型服务"),(1515,"运行反馈","现场信息")]:
        s += center(x, 715, label, 47) + center(x, 777, sub, 36, "#555")
    for a,b in [(390,570),(800,980),(1210,1390)]:
        s += arrow(f"M{a} 817 H{b}")
    s += arrow("M1515 835 V935 H1135")
    s += '<rect x="665" y="880" width="460" height="110" rx="8" fill="#edf3fb"/>'
    s += center(895, 952, "协同调度", 52, blue)
    s += arrow("M665 935 H535 V855 H695")
    s += center(900, 1050, "运行信息回到调度，推动下一轮任务分配", 39, "#555")
    finish(6, "词元供给与运行反馈闭环", "电站提供能源，设备承接任务，平台组织交易，",
           "图 6｜能源、执行、交易与反馈构成供给闭环；反馈回到调度，再影响下一轮任务安排。", s, 1100)

    from build_architecture_20261020 import article_source, revised_anchors
    original = article_source()
    if original.name.startswith("正文_用户修订稿"):
        for f in figures:
            f["after_paragraph_start"] = revised_anchors()[f["index"]]
    raw = original.read_text()
    blocks = raw.strip().split("\n\n")
    article_title = blocks[0].removeprefix("# ")
    entries, placed = [], []
    markdown = [blocks[0], "![品牌横幅](assets/masthead.png)", "\n![文章主视觉](00_文章主视觉_从绿电到词元供给.png)"]
    for block in blocks[1:]:
        if block.startswith("## "):
            entries.append(f'<h2 data-source="heading">{html.escape(block[3:])}</h2>')
        else:
            cls = ' class="note"' if block.startswith("注：") else ''
            entries.append(f'<p data-source="paragraph"{cls}>{html.escape(block)}</p>')
        markdown.append(block)
        for f in figures:
            if block.startswith(f["after_paragraph_start"]):
                stem = html.escape(f["file"])
                entries.append(f'<figure><a href="{stem}.png" target="_blank"><img src="{stem}.png" alt="{html.escape(f["title"])}" loading="lazy"></a><figcaption>{html.escape(f["caption"])}</figcaption></figure>')
                markdown.append(f'\n![{f["caption"]}]({f["file"]}.png)\n')
                placed.append(f["index"])
    assert placed == [1,2,3,4,5,6], f"Missing or reordered figure anchors: {placed}"
    markdown.append("![品牌结尾卡](assets/closing.png)")
    (output / "正文_含配图位置.md").write_text("\n\n".join(markdown)+"\n")
    (output / "配图清单.json").write_text(json.dumps({"original_sha256":hashlib.sha256(raw.encode()).hexdigest(),"figures":figures,"reference_article_counts":"unverified: both requested URLs returned HTTP 403"},ensure_ascii=False,indent=2))
    thumbs = "".join(f'<figure><a href="{html.escape(f["file"])}.png"><img src="{html.escape(f["file"])}.png" alt="{html.escape(f["title"])}"></a><figcaption>{f["index"]:02} {html.escape(f["title"])}</figcaption><p class="downloads"><a href="{html.escape(f["file"])}.png" download>PNG</a> · <a href="{html.escape(f["file"])}.svg" download>可编辑 SVG</a> · <a href="{html.escape(f["file"])}_outlined.svg" download>转曲 SVG</a></p></figure>' for f in figures)
    styles = """@font-face{font-family:Fraunces;src:url(assets/fonts/Fraunces.ttf)}@font-face{font-family:'DM Sans';src:url(assets/fonts/DM-Sans.ttf)}@font-face{font-family:'DM Mono';src:url(assets/fonts/DM-Mono.ttf)}@font-face{font-family:'Noto Serif SC';src:url(assets/fonts/Noto-serif-SC.ttf)}@font-face{font-family:'Noto Sans SC';src:url(assets/fonts/Noto-sans-SC.ttf)}
*{box-sizing:border-box}body{margin:0;background:#f8f8f8;color:#212021;font:16px/1.8 'DM Sans','Noto Sans SC',sans-serif}a{color:#2F63B8;text-underline-offset:4px}header,.gallery,.reading{max-width:1100px;margin:auto;padding:34px 24px}header h1{font:400 30px/1.5 'Noto Serif SC',serif;margin:12px 0}nav{display:flex;gap:22px;flex-wrap:wrap}.meta{font:13px/1.6 'DM Mono',monospace;color:#555}.status{padding:16px 0;border-top:1px solid #ccc;color:#555;font-size:14px}.gallery h2{font:400 28px/1.5 'Noto Serif SC',serif}.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}figure{margin:34px 0}figure img{width:100%;height:auto;display:block;background:#fff}figcaption{font-size:13px;line-height:1.8;color:#555;margin:12px 0}.downloads{font-size:13px}.article{max-width:760px;margin:auto;padding:36px 32px;background:#fff}.article h1{font:500 29px/1.55 'Noto Serif SC',serif;margin:24px 0 30px}.article h2{font:500 24px/1.65 'Noto Serif SC',serif;margin:50px 0 25px}.article p{font-size:17px;line-height:1.95;margin:25px 0;text-align:left}.article .note{font-size:14px;color:#666;border-left:2px solid #2F63B8;padding-left:15px}.article img{max-width:100%;height:auto;display:block}.article figure{margin:36px -12px}.article .caption{font-size:13px;color:#555;margin-top:10px}.article .masthead{margin-top:20px}.reading>p{max-width:760px;margin:0 auto 24px;color:#555;font-size:14px}details{margin:30px 0}summary{cursor:pointer}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px;border-bottom:1px solid #ddd;vertical-align:top}@media(max-width:700px){header,.gallery,.reading{padding:24px 16px}.grid{grid-template-columns:1fr}.article{padding:26px 20px}.article h1{font-size:25px}.article h2{font-size:23px}.article p{font-size:16px}.article figure{margin:30px -8px}}"""
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>沐仞科技 · 算电协同文章与配图</title><style>{styles}</style></head><body>
<header><div class="meta">FATHOMPEAK / ARTICLE DESIGN / 2026.10.20</div><h1>一篇正文，一张主视觉，六张解释型插图。</h1><nav><a href="#reading">完整文章预览</a><a href="#gallery">插图与下载</a><a href="fathompeak-article-20261020.zip" download>下载交付包</a><a href="正文_含配图位置.md">带配图位置的正文</a><a href="配图方案与参考阅读.md">配图方案与参考阅读范围</a></nav><p class="status">正文按用户提供版本排版。主视觉与插图为概念表达；含正文插图 6 张，加主视觉、开头横幅和结尾卡，共 9 张。两篇新参考文章读取受限，未确认其实际配图数量与位置。</p></header>
<section class="reading" id="reading"><p>以下为阅读样张。点击正文插图可查看高清图；插图和文字分开交付。</p><article class="article"><h1 data-source="title">{html.escape(article_title)}</h1><div class="meta">沐仞科技 · 品牌介绍</div><img class="masthead" src="assets/masthead.png" alt="沐仞科技固定品牌横幅"><img src="00_文章主视觉_从绿电到词元供给.png" alt="太阳能与风电连接电站侧计算设施，再向远处用户交付模型服务">{''.join(entries)}<img src="assets/closing.png" alt="沐仞科技品牌介绍和公众号二维码"></article></section>
<section class="gallery" id="gallery"><h2>主视觉与正文插图</h2><figure><img src="00_文章主视觉_从绿电到词元供给.png" alt="文章主视觉"><p class="downloads"><a href="00_文章主视觉_从绿电到词元供给.png" download>主视觉 PNG</a> · <a href="00_文章主视觉_从绿电到词元供给.svg" download>可编辑 SVG</a> · <a href="00_文章主视觉_从绿电到词元供给_outlined.svg" download>转曲 SVG</a></p></figure><div class="grid">{thumbs}</div><p>SVG 保留可编辑文字及矢量线条，版画插图为嵌入位图。转曲版将文字保存为路径。字号、文字和连接关系由代码排版。</p><p><a href="../every-v2/">返回三方向视觉对比</a></p></section></body></html>'''
    page = page.replace("../every-v2/B_开头_晨蓝拼贴.png", "assets/masthead.png").replace("../every-v2/B_结尾_晨蓝拼贴.png", "assets/closing.png")
    (output/"index.html").write_text(page)
    # The initial concept overview is archived once the editorial edition exists.
    if not (output/"architecture-editorial-v3/sources.json").exists():
        # A single sheet for comparing all seven new assets.
        overview = start(2480) + text(70,90,"从绿电到词元供给 · 文章配图",54,"#111","Noto Serif SC")
        overview += img(output/"00_文章主视觉_从绿电到词元供给.png",70,145,1000,667)
        overview += text(1150,330,"主视觉 + 六张正文图",40)
        overview += text(1150,410,"原稿保留，按概念插图",32,"#555")
        for i,f in enumerate(figures):
            x=70+(i%2)*870;y=880+(i//2)*520
            overview += img(output/(f["file"]+".png"),x,y,790,440,fit="xMidYMid meet")
            overview += text(x,y+480,f'{f["index"]:02}  {f["title"]}',30,"#333")
        save("配图总览_1800x2480",overview,2480)
    # Preserve the later BP-grounded replacement of article figures 2–4.
    if (output / "architecture-bp-v2/sources.json").exists():
        from build_architecture_20261020 import integrate_article, select_editorial
        if (output/"architecture-editorial-v3/sources.json").exists(): select_editorial()
        integrate_article()


if __name__ == "__main__" and any(flag in sys.argv for flag in ("--every", "--article")):
    try:
        build_every()
    except (OSError, subprocess.CalledProcessError, StopIteration) as error:
        raise SystemExit(f"Every directions build failed: {error}") from error
