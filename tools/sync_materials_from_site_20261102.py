"""把官网现用的素材同步进视觉素材库（projects/visual-materials），并重建素材页「全部文件下载」一节。
2026-11-02：合作方 logo 去白底裁边版、星星充电与天津能源、绿洲插画、产品页总览动画分层、网站图标。
build_site.py 依赖仓库外的源包，这里只在仓库内同步，不动其余素材。
用法：python3 tools/sync_materials_from_site_20261102.py [--check]
"""
from pathlib import Path
import html, os, shutil, sys, urllib.parse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'projects/website'
LIB = ROOT / 'projects/visual-materials'

COPY = [  # (官网来源, 素材库目标目录, 文件名筛选)
    ('art/logos', '06_第三方Logo/合作方', lambda n: n.endswith('.png')),
    ('art/oasis', '04_插画与背景/现用/绿洲', lambda n: n.endswith('.webp')),
    ('art/overview', '04_插画与背景/现用/产品页总览动画', lambda n: True),
    ('.', '04_插画与背景/现用/产品页总览动画', lambda n: n in ('ov-anim.js', 'ov-anim.css')),
    ('art/share', '05_品牌标识/现用/网站图标', lambda n: n != 'og-1200x630.png'),
    ('art/brand', '05_品牌标识/现用/网站图标', lambda n: n.endswith('_2026-10-19.svg')),
]

IMG = ('.png', '.jpg', '.jpeg', '.webp', '.svg')
VIEW = IMG + ('.pdf', '.html', '.md', '.txt', '.css', '.json')


def size(n):
    return f'{n/1048576:.1f} MB' if n >= 1048576 else f'{max(1, round(n/1024))} KB'


def files_section():
    """与 build_site.py 第 2 步同一套标记：按顶层编号文件夹、再按子目录分组。"""
    files = []
    for top in sorted(p for p in LIB.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        for root, dirs, fs in os.walk(top):
            dirs.sort(); fs.sort()
            for f in fs:
                if f.startswith('.'): continue
                files.append(os.path.relpath(os.path.join(root, f), LIB))
    groups = {}
    for rel in files:
        parts = rel.split(os.sep)
        groups.setdefault(parts[0], {}).setdefault(os.sep.join(parts[1:-1]), []).append(rel)
    total = sum(os.path.getsize(LIB / r) for r in files)
    out = ['<section id="files"><h2>全部文件下载</h2>',
           f'<p class="lede">{len(files)} 个文件，共 {size(total)}。点「下载」直接保存原文件；图片、PDF 也可以点「打开」先看。在微信里打开本页的话，先点右上角 ··· 选「在浏览器打开」再下载，图片可以长按保存。</p>',
           '<nav class="fchips" aria-label="文件夹">' + ''.join(f'<a href="#f-{i}">{html.escape(t)}</a>' for i, t in enumerate(groups)) + '</nav>']
    for i, (top, subs) in enumerate(groups.items()):
        out.append(f'<div class="fgrp" id="f-{i}"><h3>{html.escape(top)} <span>{sum(len(v) for v in subs.values())} 个文件</span></h3>')
        for sub, rels in subs.items():
            if sub: out.append(f'<p class="fsub">{html.escape(sub)}</p>')
            out.append('<ul class="flist">')
            for rel in rels:
                name = os.path.basename(rel); url = urllib.parse.quote(rel.replace(os.sep, '/')); ext = os.path.splitext(name)[1].lower()
                th = f'<img src="{url}" alt="" loading="lazy">' if ext in IMG else f'<span class="fext">{html.escape(ext[1:].upper())}</span>'
                op = f'<a class="fo" href="{url}" target="_blank" rel="noopener">打开</a>' if ext in VIEW else '<span class="fo"></span>'
                out.append(f'<li><span class="fth">{th}</span><span class="fn">{html.escape(name)}</span><span class="fs">{size(os.path.getsize(LIB / rel))}</span>{op}<a class="fd" href="{url}" download="{html.escape(name)}">下载</a></li>')
            out.append('</ul>')
        out.append('</div>')
    out.append('</section>')
    return '\n'.join(out), len(files)


def ul(rel_dir):
    """一个子目录的文件列表 <ul>，标记与 build_site.py 相同。"""
    d = LIB / rel_dir; out = ['<ul class="flist">']
    for f in sorted(x for x in d.iterdir() if x.is_file() and not x.name.startswith('.')):
        rel = f'{rel_dir}/{f.name}'; name = f.name; url = urllib.parse.quote(rel); ext = f.suffix.lower()
        th = f'<img src="{url}" alt="" loading="lazy">' if ext in IMG else f'<span class="fext">{html.escape(ext[1:].upper())}</span>'
        op = f'<a class="fo" href="{url}" target="_blank" rel="noopener">打开</a>' if ext in VIEW else '<span class="fo"></span>'
        out.append(f'<li><span class="fth">{th}</span><span class="fn">{html.escape(name)}</span><span class="fs">{size(f.stat().st_size)}</span>{op}<a class="fd" href="{url}" download="{html.escape(name)}">下载</a></li>')
    out.append('</ul>')
    return '\n'.join(out)


def main():
    """只改受影响的分组，页面其余部分不动（全量重建会带出页面原本未列出的文件）。"""
    import re
    page = LIB / 'index.html'
    s = page.read_text(encoding='utf-8')
    if '现用/产品页总览动画' in s: sys.exit('[停止] 已同步过')
    copied = []
    for src, dst, ok in COPY:
        d = LIB / dst; d.mkdir(parents=True, exist_ok=True)
        for f in sorted((SITE / src).iterdir()):
            if f.is_file() and ok(f.name):
                shutil.copy2(f, d / f.name); copied.append(f'{dst}/{f.name}')
    added = 0; added_bytes = 0

    def group(top):
        i = s.index(f'<h3>{top} <span>'); j = s.index('<div class="fgrp"', i) if '<div class="fgrp"' in s[i:] else s.index('</section>', i)
        return i, j

    # 1 合作方：整张列表替换
    q = urllib.parse.quote('06_第三方Logo/合作方/')
    i = s.index('<p class="fsub">合作方</p>'); a = s.index('<ul class="flist">', i); b = s.index('</ul>', a) + 5
    old_n = s[a:b].count('<li>'); new = ul('06_第三方Logo/合作方'); added += new.count('<li>') - old_n
    added_bytes += sum(f.stat().st_size for f in (LIB / '06_第三方Logo/合作方').iterdir())
    s = s[:a] + new + s[b:]
    # 2 新子目录：插到所属分组末尾
    for top, sub in (('04_插画与背景', '现用/绿洲'), ('04_插画与背景', '现用/产品页总览动画'), ('05_品牌标识', '现用/网站图标')):
        i, j = group(top)
        end = s.rindex('</div>', i, j)
        block = f'\n<p class="fsub">{html.escape(sub)}</p>\n' + ul(f'{top}/{sub}') + '\n'
        n = block.count('<li>'); added += n
        added_bytes += sum(f.stat().st_size for f in (LIB / top / sub).iterdir())
        s = s[:end] + block + s[end:]
    # 3 分组计数
    for top in ('04_插画与背景', '05_品牌标识', '06_第三方Logo'):
        i, j = group(top)
        n = s[i:j].count('<li>')
        s = re.sub(rf'(<h3>{top} <span>)\d+( 个文件</span>)', rf'\g<1>{n}\g<2>', s, count=1)
    # 4 总数
    m = re.search(r'<p class="lede">(\d+) 个文件，共 ([\d.]+) MB。', s)
    total = int(m.group(1)) + added
    s = s.replace(m.group(0), f'<p class="lede">{total} 个文件，共 {float(m.group(2)) + added_bytes / 1048576 * 0:.1f} MB。', 1)
    page.write_text(s, encoding='utf-8')
    print(len(copied), 'files synced;', added, 'list rows added; total', total)


if __name__ == '__main__':
    main()
