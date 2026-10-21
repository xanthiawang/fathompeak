"""Build the UI visual package as a static download site (GitHub Pages).
Source: ../UI视觉交付包_2026-10-16 (left untouched). Output: this folder.
index.html = the package's own 00_先看这个.html + a per-file download section, a WeChat hint and noindex.
Usage: python3 build_site.py"""
import os, re, shutil, html, urllib.parse, json, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'UI视觉交付包_2026-10-16')
EXCLUDE = set(json.loads(os.environ.get('EXCLUDE', '[]')))   # folders or files to leave out, e.g. ["08_参考与历史文档"]


def publish_logo_palette(root):
    """Document the approved neutral logo materials without changing UI colors."""
    values = [
        ("--logo-black", "#000000", "字标黑"),
        ("--logo-shadow", "#111111", "峰面深影"),
        ("--logo-graphite", "#404040", "石墨灰"),
        ("--logo-mid", "#777777", "过渡灰"),
        ("--logo-silver", "#A1A1A1", "银灰"),
        ("--logo-light", "#DFDFDF", "亮面灰"),
        ("--logo-highlight", "#F8F8F8", "峰面高光"),
        ("--logo-white", "#FFFFFF", "白底"),
    ]
    token_file = root / "01_色彩与字体/tokens.json"
    data = json.loads(token_file.read_text())
    data["色彩"]["Logo 中性色 · 2026-10-20"] = {key: {"值": color, "用途": label} for key, color, label in values}
    source = root / "05_品牌标识/现用/官方logo_2026-10-18/primary.svg"
    ns = {"s": "http://www.w3.org/2000/svg"}
    data["Logo 渐变"] = {
        "说明": "从确认版 primary.svg 提取的原始五个渐变；Logo 保持中性灰。晨蓝和暮紫用于版面、插画和强调信息，不替换 Logo 内部颜色。",
        "来源": str(source.relative_to(root)),
        "定义": [{**g.attrib, "stops": [stop.attrib for stop in g]} for g in ET.parse(source).findall(".//s:linearGradient", ns)],
    }
    token_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    css_file = root / "01_色彩与字体/tokens.css"
    css = re.sub(r"\n/\* LOGO_NEUTRALS_START \*/.*?/\* LOGO_NEUTRALS_END \*/\n?", "", css_file.read_text(), flags=re.S)
    css += "\n/* LOGO_NEUTRALS_START */\n:root{\n" + "".join(f"  {key}:{color}; /* {label} */\n" for key, color, label in values) + "}\n/* LOGO_NEUTRALS_END */\n"
    css_file.write_text(css)
    page = root / "index.html"
    content = re.sub(r'<!-- LOGO_PALETTE_START -->.*?<!-- LOGO_PALETTE_END -->', '', page.read_text(), flags=re.S)
    panel = '<!-- LOGO_PALETTE_START --><div id="logo-palette"><h3>Logo 中性色与金属渐变</h3><p class="lede">已确认的 Logo 使用黑、白与中性灰。以下为原稿中的主要灰阶锚点；晨蓝和暮紫继续用于界面、插画及强调信息。Logo 原始五组曲面渐变已收录到 tokens.json，按原 SVG 使用。</p><div class="sws">'
    for key, color, label in values:
        panel += f'<div class="sw"><i style="background:{color}"></i><b>{color}</b><span>{key}</span><p>{label}</p></div>'
    panel += '</div></div><!-- LOGO_PALETTE_END -->'
    content = content.replace('<section id="color"><h2>色彩</h2>', '<section id="color"><h2>色彩</h2>' + panel)
    page.write_text(content)



def publish_logo():
    """Update only the approved brand assets; leave other UI materials intact."""
    root = Path(HERE)
    source = root.parent / 'Logo重新设计_Every参考_2026-10-17' / '层叠峰面_中英字标统一_v31_2026-10-20'
    brand = root / '05_品牌标识'
    dest = brand / '现用' / '官方logo_2026-10-18'
    avatar = source
    names = [f'{name}.{ext}' for name in ('overview', 'primary', 'circle', 'square', 'symbol', 'wordmark-zh', 'wordmark-en', 'wechat-avatar-single-line-1024') for ext in ('svg', 'png')]
    names += ['README.md', 'validation.json']
    # Validate all inputs before touching existing files.
    inputs = [source / name for name in names] + [avatar / f'wechat-avatar-1024.{ext}' for ext in ('svg', 'png')]
    for item in inputs:
        if not item.is_file():
            raise FileNotFoundError(f'Approved logo source missing: {item}')
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(source / name, dest / name)
    for ext in ('svg', 'png'):
        shutil.copy2(avatar / f'wechat-avatar-1024.{ext}', dest / f'wechat-avatar-1024.{ext}')
    # Retain the previous website mark and application assets as history.
    history = brand / '旧版_2026-10-20前'
    history.mkdir(exist_ok=True)
    for name in ('沐仞山形标_现用.svg', 'favicon.svg', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'og-1200x630.png'):
        old = brand / '现用' / name
        if old.exists():
            target = history / name.replace('_现用', '_旧版')
            if target.exists() and target.read_bytes() != old.read_bytes():
                raise FileExistsError(f'History conflict: {target}')
            shutil.move(str(old), str(target))
    bundle = dest / 'fathompeak-logo-20261020.zip'
    with ZipFile(bundle, 'w', ZIP_DEFLATED) as z:
        for f in sorted(dest.iterdir()):
            if f.is_file() and f.suffix != '.zip': z.write(f, f.name)
    def url(path): return urllib.parse.quote(str(path.relative_to(root)))
    def card(name, title, description):
        return f'<figure><a href="{url(dest / (name + ".svg"))}"><img src="{url(dest / (name + ".png"))}" alt="{title} — FATHOMPEAK 沐仞科技" loading="lazy" style="aspect-ratio:4/3;object-fit:contain;padding:24px;background:#fff"></a><figcaption><b>{title}</b>{description}<br><a href="{url(dest / (name + ".svg"))}" download>下载 SVG</a> · <a href="{url(dest / (name + ".png"))}" download>下载 PNG</a></figcaption></figure>'
    page = root / 'index.html'
    text = page.read_text()
    old_section = re.search(r'<section id="brand">.*?</section>', text, re.S).group()
    archive = old_section[old_section.index('<h3>Logo 探索稿'):] if '<h3>Logo 探索稿' in old_section else ''
    archive = archive.removesuffix('</section>').removesuffix('</details>')
    archive = re.sub(r'<p class="lede">10-14.*?</p>', '<p class="lede">定稿前的探索方向，仅作历史参考；正式使用以上「层叠峰面」版本。</p>', archive, count=1, flags=re.S)
    content = '<section id="brand"><h2>品牌标识 · 沐仞科技</h2><p class="lede">已确认的「层叠峰面」Logo：黑白灰图形 + FATHOMPEAK 英文字标 + 沐仞科技。主标、圆形、方形与独立图形均提供可编辑 SVG 和 PNG，字标已转曲，无需安装字体。字标 v31：英文直接提取自指定图二，中文四字按同一参考统一笔形与字重；使用矢量字标，不用普通字体替代。素材更新：2026-10-20。</p>'
    content += f'<div class="dl" style="margin-bottom:24px"><a class="hbtn" href="{url(bundle)}" download>下载 Logo 整包 · SVG + PNG</a><a href="{url(dest / "wechat-avatar-1024.png")}" download>下载微信头像 · 1024 × 1024</a></div>'
    content += f'<figure style="margin-bottom:20px"><a href="{url(dest / "overview.svg")}" style="background:#fff"><img src="{url(dest / "overview.png")}" alt="沐仞科技 Logo 主标、圆形和方形版本总览" style="max-height:none"></a><figcaption>Logo 组合总览 · 统一黑白灰，白底展示</figcaption></figure><div class="arts">'
    for args in [('wechat-avatar-single-line-1024','英文单行版','FATHOMPEAK 单行排列，1024 × 1024 白底，保留山形和中文。'),('primary','主标组合','峰面图形 + FATHOMPEAK + 沐仞科技。'),('circle','圆形版本','圆形容器，保留完整品牌组合。'),('square','方形版本','圆角方形容器，保留完整品牌组合。'),('symbol','独立图形','用于紧凑空间，保留原有峰面层次。'),('wechat-avatar-1024','微信头像','1024 × 1024 PNG，纯白不透明背景。')]: content += card(*args)
    content += '</div><p style="margin-top:24px"><a href="09_公众号视觉/2026-10-20/every-v2/">公众号横版视觉：Every 风格三方向对比 →</a> · <a href="09_公众号视觉/2026-10-20/article-compute-energy/">算电协同品牌文章与完整配图 →</a></p><details style="margin-top:28px"><summary>历史探索稿（非当前 Logo）</summary>' + archive + '</details></section>'
    text = text.replace(old_section, content)
    text = re.sub(r'<p><b>Logo：</b>.*?</p>', '', text)
    text = text.replace('全部取自线上版本 c5c5450（2026-10-16）', 'UI 基础素材取自线上版本 c5c5450（2026-10-16），品牌标识已补充为确认的层叠峰面版本（2026-10-20）')
    if 'Logo 与微信头像 ↓' not in text: text = text.replace('href="#files">下载文件 ↓</a>', 'href="#files">下载文件 ↓</a> <a class="hbtn" href="#brand">Logo 与微信头像 ↓</a>')
    # Refresh the brand folder count and its per-file download list.
    brand_files = sorted(f for f in brand.rglob('*') if f.is_file() and not f.name.startswith('.'))
    text = re.sub(r'(<td class="mono">05_品牌标识</td><td class="mono">).*?(</td><td>).*?</td>', lambda m: m[1] + str(len(brand_files)) + m[2] + '已确认的层叠峰面 Logo：主标、圆形、方形、独立图形、微信头像，附 SVG / PNG 和整包下载；旧标与探索稿保留为历史。</td>', text, count=1)
    listing = f'<div class="fgrp" id="f-4"><h3>05_品牌标识 <span>{len(brand_files)} 个文件</span></h3>'
    for folder in sorted(set(f.parent for f in brand_files)):
        listing += f'<p class="fsub">{folder.relative_to(brand)}</p><ul class="flist">'
        for f in [x for x in brand_files if x.parent == folder]:
            thumb = f'<img src="{url(f)}" alt="" loading="lazy">' if f.suffix in ('.png','.svg') else f'<span class="fext">{f.suffix[1:].upper()}</span>'
            listing += f'<li><span class="fth">{thumb}</span><span class="fn">{f.name}</span><span class="fs">{max(1, round(f.stat().st_size/1024))} KB</span><a class="fo" href="{url(f)}" target="_blank" rel="noopener">打开</a><a class="fd" href="{url(f)}" download>下载</a></li>'
        listing += '</ul>'
    listing += '</div>'
    text = re.sub(r'<div class="fgrp" id="f-4">.*?(?=<div class="fgrp" id="f-5">)', lambda _: listing, text, count=1, flags=re.S)
    all_files = [f for folder in root.iterdir() if folder.is_dir() and folder.name[:2] in ('01','02','03','04','05','06','07','08') for f in folder.rglob('*') if f.is_file() and not f.name.startswith('.')]
    total = sum(f.stat().st_size for f in all_files)
    text = re.sub(r'(<section id="files"><h2>全部文件下载</h2>\s*<p class="lede">).*?。', lambda m: m[1] + f'{len(all_files)} 个文件，共 {total/1048576:.1f} MB。', text, count=1, flags=re.S)
    page.write_text(text)
    publish_logo_palette(root)
    print(f'Published approved logo assets: {len(brand_files)} brand files; {bundle.name}')

if '--logo-only' in sys.argv:
    try:
        publish_logo()
    except (OSError, ValueError, AttributeError) as error:
        raise SystemExit(f'Logo publication failed: {error}') from error
    raise SystemExit(0)

# 1. copy files (everything except the old index page)
for name in os.listdir(HERE):
    p = os.path.join(HERE, name)
    if name[:2].isdigit() and os.path.isdir(p) and os.path.isdir(os.path.join(SRC, name)): shutil.rmtree(p)
files = []
for root, dirs, fs in os.walk(SRC):
    dirs.sort(); fs.sort()
    for f in fs:
        if f.startswith('.') or f == '00_先看这个.html': continue
        rel = os.path.relpath(os.path.join(root, f), SRC)
        if any(rel == e or rel.startswith(e + os.sep) for e in EXCLUDE): continue
        dst = os.path.join(HERE, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(root, f), dst); files.append(rel)

def size(n):
    return f'{n/1048576:.1f} MB' if n >= 1048576 else f'{max(1, round(n/1024))} KB'
IMG = ('.png', '.jpg', '.jpeg', '.webp', '.svg')
VIEW = IMG + ('.pdf', '.html', '.md', '.txt', '.css', '.json')

# 2. file section, grouped by folder then subfolder
groups = {}
for rel in files:
    parts = rel.split(os.sep); top = parts[0]; sub = os.sep.join(parts[1:-1])
    groups.setdefault(top, {}).setdefault(sub, []).append(rel)
total = sum(os.path.getsize(os.path.join(HERE, r)) for r in files)
out = ['<section id="files"><h2>全部文件下载</h2>',
       f'<p class="lede">{len(files)} 个文件，共 {size(total)}。点「下载」直接保存原文件；图片、PDF 也可以点「打开」先看。在微信里打开本页的话，先点右上角 ··· 选「在浏览器打开」再下载，图片可以长按保存。</p>',
       '<nav class="fchips" aria-label="文件夹">' + ''.join(f'<a href="#f-{i}">{html.escape(t)}</a>' for i, t in enumerate(groups)) + '</nav>']
for i, (top, subs) in enumerate(groups.items()):
    n = sum(len(v) for v in subs.values())
    out.append(f'<div class="fgrp" id="f-{i}"><h3>{html.escape(top)} <span>{n} 个文件</span></h3>')
    for sub, rels in subs.items():
        if sub: out.append(f'<p class="fsub">{html.escape(sub)}</p>')
        out.append('<ul class="flist">')
        for rel in rels:
            name = os.path.basename(rel); url = urllib.parse.quote(rel.replace(os.sep, '/')); ext = os.path.splitext(name)[1].lower()
            th = f'<img src="{url}" alt="" loading="lazy">' if ext in IMG else f'<span class="fext">{html.escape(ext[1:].upper())}</span>'
            op = f'<a class="fo" href="{url}" target="_blank" rel="noopener">打开</a>' if ext in VIEW else '<span class="fo"></span>'
            out.append(f'<li><span class="fth">{th}</span><span class="fn">{html.escape(name)}</span><span class="fs">{size(os.path.getsize(os.path.join(HERE, rel)))}</span>{op}<a class="fd" href="{url}" download="{html.escape(name)}">下载</a></li>')
        out.append('</ul>')
    out.append('</div>')
out.append('</section>')
FILES = '\n'.join(out)

CSS = '''<style id="site-dl">
.wx{display:none;position:sticky;top:0;z-index:20;background:#212021;color:#fff;font-size:14px;line-height:1.5;padding:10px 16px;text-align:center} .wx.on{display:block}
.toc a.dlk{font-weight:600;color:var(--ink)}
.hbtn{display:inline-flex;align-items:center;height:44px;padding:0 22px;border-radius:999px;background:#000;color:#fff;text-decoration:none;font-weight:500;margin-top:20px}
.fchips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px} .fchips a{font:400 13px var(--mono);text-decoration:none;color:var(--ink);background:rgba(255,255,255,.86);border:1px solid var(--line);border-radius:999px;padding:5px 12px}
.fgrp{margin:0 0 26px} .fgrp h3{font:500 15px var(--mono);margin:0 0 6px} .fgrp h3 span{font-weight:400;color:var(--ink-50);font-size:13px;margin-left:6px}
.fsub{font:400 12px var(--mono);color:var(--ink-50);margin:12px 0 4px}
.flist{list-style:none;margin:0;padding:0;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden}
.flist li{display:grid;grid-template-columns:44px minmax(0,1fr) auto auto auto;align-items:center;gap:12px;padding:8px 12px;border-top:1px solid rgba(61,49,79,.08)} .flist li:first-child{border-top:0}
.fth{width:44px;height:32px;border-radius:6px;background:#F3F1EA;display:grid;place-items:center;overflow:hidden} .fth img{max-width:100%;max-height:100%;object-fit:contain}
.fext{font:500 10px var(--mono);color:var(--ink-50)}
.fn{font:400 13.5px var(--mono);overflow:hidden;text-overflow:ellipsis;white-space:nowrap} .fs{font:400 12px var(--mono);color:var(--ink-50)}
.fo{font-size:13px;color:var(--accent)} .fd{display:inline-flex;align-items:center;height:30px;padding:0 14px;border-radius:999px;background:#000;color:#fff;text-decoration:none;font-size:13px;font-weight:500}
@media (max-width:640px){.flist li{grid-template-columns:40px minmax(0,1fr) auto;row-gap:4px} .fs{grid-column:2} .fo{grid-column:3;grid-row:2;justify-self:end} .fd{grid-column:3;grid-row:1}}
</style>'''
WX = '<div class="wx" id="wx">微信里不能直接下载文件：点右上角 ··· 选「在浏览器打开」再下载。图片可以长按保存。</div>'
JS = "<script>if(/MicroMessenger/i.test(navigator.userAgent))document.getElementById('wx').classList.add('on')</script>"

# 3. assemble index.html
s = open(os.path.join(SRC, '00_先看这个.html'), encoding='utf-8').read()
def once(a, b, label):
    global s
    assert s.count(a) == 1, (label, s.count(a)); s = s.replace(a, b)
once('</head>', '<meta name="robots" content="noindex,nofollow">\n' + CSS + '\n</head>', 'head')
if 'name="viewport"' not in s: s = s.replace('<meta name="robots"', '<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="robots"', 1)
once('<body>', '<body>\n' + WX, 'body')
once('<a href="https://xanthiawang.github.io/fathompeak-site/">xanthiawang.github.io/fathompeak-site</a>。</p></div></header>',
     '<a href="https://xanthiawang.github.io/fathompeak-site/">xanthiawang.github.io/fathompeak-site</a>。</p><a class="hbtn" href="#files">下载文件 ↓</a></div></header>', 'header btn')
once('<b>目录</b><a href="#pkg">包里有什么</a>', '<b>目录</b><a class="dlk" href="#files">全部文件下载</a><a href="#pkg">包里有什么</a>', 'toc')
i = s.index('<section id="rules">'); s = s[:i] + FILES + s[i:]
once('</body>', JS + '\n</body>', 'js')
# links in the original page that point at files: make them download-safe URLs (percent-encode)
s = re.sub(r'(href|src)="((?!https?:|#|data:|mailto:)[^"]+)"', lambda m: f'{m.group(1)}="{urllib.parse.quote(m.group(2), safe="/#.%")}"', s)
# say so in the guide when a file is left out of the web version
for e in EXCLUDE:
    name = os.path.basename(e)
    if name in s: s = s.replace('<b>' + name + '</b>', '<b>' + name + '</b>（不在网页版里，需要的话找 Zixin 要）', 1)
    s = s.replace('、竞品视觉调研板。部分内容已过时', '。部分内容已过时', 1) if '竞品' in e else s
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(s)
open(os.path.join(HERE, '.nojekyll'), 'w').close()
missing = [m for m in re.findall(r'(?:href|src)="((?!https?:|#|data:|mailto:)[^"]+)"', s) if not os.path.exists(os.path.join(HERE, urllib.parse.unquote(m)))]
print('files', len(files), 'total', size(total), 'broken local links', len(missing), missing[:5])

# Always preserve the approved logo when regenerating the full material site.
publish_logo()
