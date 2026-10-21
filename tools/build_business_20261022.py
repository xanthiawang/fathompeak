"""Format the supplied business article; preserve its text and approved branding."""
from pathlib import Path
from functools import lru_cache
import argparse, base64, copy, hashlib, html, json, logging, re, shutil, subprocess, zipfile
from lxml import etree as E, html as H
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools import subset
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'publications/business'
A=OUT/'assets'
TITLE='沐仞科技｜绿色算力部署与模型 API 服务，开放合作'
ZIP='fathompeak-business-20261022.zip'
FONT=None
SOURCE=None

@lru_cache(maxsize=4)
def face(weight):
    data=FONT.read_bytes();font=hb.Font(hb.Face(data));font.set_variations({'wght':weight})
    tt=TTFont(FONT);return font,tt.getGlyphSet(location={'wght':weight}),tt.getGlyphOrder()

def txt(text,x,y,size,weight=400,fill='#212021',anchor='start'):
    font,glyphs,order=face(weight);buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(font,buf)
    scale=size/font.face.upem;width=sum(p.x_advance for p in buf.glyph_positions)*scale
    if anchor=='middle':x-=width/2
    paths=[];cursor=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        pen=SVGPathPen(glyphs);glyphs[order[info.codepoint]].draw(pen)
        paths.append(f'<path transform="translate({x+(cursor+pos.x_offset)*scale} {y-pos.y_offset*scale}) scale({scale} {-scale})" d="{pen.getCommands()}"/>');cursor+=pos.x_advance
    return f'<g aria-label="{html.escape(text)}" fill="{fill}">'+''.join(paths)+'</g>'

def raster(name,x,y,w,h):
    data=base64.b64encode((A/name).read_bytes()).decode()
    return f'<image href="data:image/png;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>'

def logo(name,x,y,w):
    el=E.parse(str(A/name)).getroot();v=list(map(float,el.get('viewBox').split()));el.set('x',str(x));el.set('y',str(y));el.set('width',str(w));el.set('height',str(w*v[3]/v[2]));return E.tostring(el,encoding='unicode')

def svg(name,height,body):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" viewBox="0 0 1800 {height}"><title>沐仞科技 · {name}</title><rect width="1800" height="{height}" fill="white"/>'+body+'</svg>'
    f=A/(name+'.svg');f.write_text(s)
    subprocess.run(['rsvg-convert',str(f),'-o',str(f.with_suffix('.png'))],check=True)

def cards():
    s=raster('landscape.png',0,0,1800,1013)
    s+='<rect x="390" y="88" width="1020" height="525" fill="white" stroke="#2F63B8" stroke-width="3"/><path d="M390 128H1410" stroke="#2F63B8" stroke-width="2.5"/>'
    for x in [411,433,455]:s+=f'<circle cx="{x}" cy="108" r="5" fill="none" stroke="#2F63B8" stroke-width="2"/>'
    s+=txt('从绿色电力',900,297,78,600,anchor='middle')+txt('到模型服务',900,408,78,600,anchor='middle')
    s+=txt('GPU 部署 · 统一调度 · 模型 API',900,509,31,anchor='middle')
    svg('opening',1013,s)
    s=raster('stamp-art.png',0,0,1800,900)
    for x,label,color in [(300,'词元工厂','#FFFAEB'),(900,'协同调度','#212021'),(1500,'模型 API','#FFFAEB')]:s+=txt(label,x,175,58,600,color,'middle')
    svg('business-stamps',900,s)
    s=raster('landscape.png',0,0,1800,1013)
    s+='<rect x="0" y="0" width="1110" height="850" fill="white"/>'
    s+=logo('symbol.svg',75,67,80)+logo('wordmark-en.svg',175,83,310)+logo('wordmark-zh.svg',520,82,125)
    s+=txt('一起，连接',75,300,76,600)+txt('能源与计算。',75,405,76,600)
    s+=txt('电站与设备合作 · 模型服务采购 · 技术研发',80,507,29)
    s+=txt('www.fathompeak.cn',80,644,29,fill='#2F63B8')
    s+=txt('商务合作  fathompeak@163.com',80,708,28,fill='#555555')
    s+='<rect x="1362" y="370" width="355" height="358" fill="white"/>'
    s+=raster('wechat-qr.png',1396,388,286,286)+txt('扫码关注沐仞科技',1540,708,25,anchor='middle')
    svg('closing',850,s)

def blocks():
    lines=[x.strip() for x in SOURCE.read_text().splitlines() if x.strip() and x.strip()!='\u200b']
    items=[];changes=[];bullet=False
    subs=['创始人：路畅','技术团队','商业与国际市场团队','创新创业赛事','团队荣誉','学术研究','媒体关注','能源与电站合作','算力设备与基础设施合作','模型服务与企业客户合作','技术研发与产业合作']
    for i,t in enumerate(lines):
        if t=='•':bullet=True;continue
        original=t
        if i==0:t=TITLE
        if t.startswith('合作咨询：'):t='合作咨询： fathompeak@163.com'
        if t.startswith('官方网站：'):t='官方网站： www.fathompeak.cn'
        if t!=original:changes.append({'source':original,'rendered':t})
        kind='title' if i==0 else 'section' if re.match(r'^[一二三四五六七]、',t) else 'subheading' if t in subs or re.match(r'^[123]\. ',t) else 'minor' if t.startswith(('Tapestrix：','NetWeaver：','第一，','第二，','第三，')) or t=='算电协同调度系统' else 'li' if bullet else 'paragraph'
        items.append({'kind':kind,'text':t,'source':original});bullet=False
    return items,changes

def inline(t):
    s=html.escape(t)
    if t.startswith('官方网站：'):return '官方网站： <a href="https://www.fathompeak.cn/">www.fathompeak.cn</a>'
    if t.startswith('合作咨询：'):return '合作咨询： <a href="mailto:fathompeak@163.com">fathompeak@163.com</a>'
    for phrase in ['AI基础设施、算电协同与分布式算力网络','前店后厂','设备部署、技术运营与算力资源协同合作','高效、可靠、具有成本竞争力']:
        s=s.replace(phrase,'<strong>'+phrase+'</strong>')
    return s

CSS="""
@font-face{font-family:'DM Sans';src:url('assets/fonts/DM-Sans.ttf')}@font-face{font-family:'Noto Sans SC';src:url('assets/fonts/NotoSansSC-Regular.woff2');font-weight:400;font-display:swap}@font-face{font-family:'Noto Sans SC';src:url('assets/fonts/NotoSansSC-Semibold.woff2');font-weight:600;font-display:swap}
*{box-sizing:border-box}html{scroll-behavior:auto}body{margin:0;color:#212021;background:#f7f7f5;font:16px/1.9 'DM Sans','Noto Sans SC',sans-serif}a{color:#2f63b8;text-underline-offset:4px;text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,button:focus-visible{outline:2px solid #2f63b8;outline-offset:4px}::selection{background:#dce9ff;color:#212021}button{font:inherit;color:inherit;cursor:pointer}button:disabled{opacity:.5;cursor:wait}.toolbar{max-width:936px;margin:20px auto 16px;padding:0 24px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center;font-size:12px}.toolbar button{background:white;border:1px solid #ccc;padding:5px 12px;border-radius:2px}.toolbar .back{margin-right:auto}.status{min-height:20px;width:100%;color:#555}.article{max-width:936px;margin:0 auto;background:#fff;padding:42px 68px 48px;font-size:17px;line-height:1.95}.brandline{display:flex;gap:14px;align-items:center;padding-bottom:22px;border-bottom:1px solid #e3e3e3}.article .brandline img{width:48px;height:auto;flex:0 0 auto}.article .brandline .en{width:175px}.article .brandline .zh{width:76px}.article h1{font-size:27px;line-height:1.65;font-weight:600;margin:28px 0 22px;text-wrap:pretty}.article h2{font-size:20px;line-height:1.7;font-weight:600;margin:44px 0 22px;scroll-margin-top:24px}.article h3{font-size:17px;line-height:1.8;font-weight:600;margin:29px 0 13px}.article h4{font-size:16px;line-height:1.8;font-weight:600;margin:25px 0 10px}.article p{margin:0 0 21px}.article strong{font-weight:600}.article ul{padding-left:1.4em;margin:0 0 23px}.article li{margin:0 0 11px;padding-left:3px}.article li::marker{color:#888}.article figure{margin:27px 0 32px}.article figure.hero{margin:10px -20px 30px}.article img{display:block;max-width:100%;height:auto;width:100%}.article figcaption{font-size:12px;line-height:1.75;color:#666;margin-top:9px;text-align:center}.article .contacts{margin-top:37px;padding-top:2px;border-top:1px solid #ddd;font-size:13px;line-height:1.85}.article .contacts h2{font-size:16px;margin:21px 0 16px}.article .contacts p{margin:0 0 9px}.article .closing{margin:30px -15px 0}.downloads{max-width:936px;margin:32px auto 50px;padding:0 24px;font-size:13px}.downloads h2{font-size:18px;font-weight:600}.downloads p{margin:10px 0}.asset-list{display:grid;grid-template-columns:1fr 1fr;gap:24px}.asset-list img{width:100%;height:190px;object-fit:contain;background:white}.asset-list h3{font-size:14px;margin:10px 0 5px}.asset-list a{margin-right:18px}.note{font-size:12px;color:#666;margin-top:24px!important}.article .contacts .endline{margin-top:20px}
@media(max-width:700px){.toolbar{padding:0 20px;margin:13px auto 12px}.article{padding:25px 23px 34px;font-size:16px;line-height:1.95}.brandline{gap:10px;padding-bottom:18px}.article .brandline img{width:35px}.article .brandline .en{width:138px}.article .brandline .zh{width:60px}.article h1{font-size:23px;line-height:1.65;margin:23px 0 18px}.article h2{font-size:19px;margin:35px 0 20px}.article h3{font-size:17px;margin-top:26px}.article h4{font-size:16px}.article figure.hero{margin:4px -13px 25px}.article figure{margin:23px -5px 27px}.article .contacts{font-size:13px}.article .contacts h2{font-size:16px}.article .closing{margin:24px -12px 0}.asset-list{grid-template-columns:1fr}.asset-list img{height:auto}.downloads{padding:0 23px}}
@media print{body{background:white}.toolbar,.downloads{display:none}.article{padding:0;max-width:none;font-size:11pt}.article h1{font-size:22pt}h2,h3,h4{break-after:avoid}figure{break-inside:avoid}}
"""

JS="""
const reading=document.getElementById('reading'),status=document.getElementById('copy-status');
document.getElementById('copy-text').addEventListener('click',async()=>{try{const text=await (await fetch('正文_排版稿_2026-10-22.txt')).text();await navigator.clipboard.writeText(text);status.textContent='正文已复制。';}catch(e){status.textContent='复制未完成，请下载纯文字稿，或选中文字复制。';}});
document.getElementById('copy-rich').addEventListener('click',async()=>{try{const clone=reading.cloneNode(true),original=[reading,...reading.querySelectorAll('*')],nodes=[clone,...clone.querySelectorAll('*')];original.forEach((el,i)=>{const s=getComputedStyle(el);for(const k of ['display','align-items','gap','font-size','font-weight','line-height','color','text-align','margin-top','margin-bottom','padding-top','padding-bottom','border-top','border-bottom'])nodes[i].style.setProperty(k,s.getPropertyValue(k));});clone.style.cssText='font-family:"PingFang SC","Noto Sans SC",sans-serif;color:#212021;line-height:1.95;font-size:16px;max-width:100%;padding:0;margin:0;';clone.querySelectorAll('img').forEach((img,imageIndex)=>{img.src=new URL(img.getAttribute('src'),location.href).href;img.style.maxWidth='100%';img.style.height='auto';if(!img.closest('.brandline'))img.style.width='100%';else img.style.width=getComputedStyle(reading.querySelectorAll('img')[imageIndex]).width;});clone.querySelectorAll('a').forEach(a=>a.href=new URL(a.getAttribute('href'),location.href).href);await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([clone.outerHTML],{type:'text/html'}),'text/plain':new Blob([reading.innerText],{type:'text/plain'})})]);status.textContent='图文已复制，可粘贴到编辑器；请检查目标平台的字体与图片显示。';}catch(e){status.textContent='图文复制未完成，可下载整包或复制纯文字。';}});
"""

def fonts(items):
    dest=A/'fonts';dest.mkdir(exist_ok=True)
    src=ROOT/'projects/visual-materials/09_公众号视觉/2026-10-20/article-compute-energy/assets/fonts'
    for name in ['DM-Sans.ttf','dmsans-OFL.txt','notosanssc-OFL.txt']:shutil.copy2(src/name,dest/name)
    chars=''.join(x['text'] for x in items)+TITLE+'阅读复制图文正文已完成合作服务'
    for weight,name in [(400,'NotoSansSC-Regular.woff2'),(600,'NotoSansSC-Semibold.woff2')]:
        f=instantiateVariableFont(TTFont(FONT),{'wght':weight},inplace=True);sub=subset.Subsetter();sub.populate(text=chars);sub.subset(f);f.flavor='woff2';f.save(dest/name)

def page(items,changes):
    chunks=['<header class="brandline"><img src="assets/symbol.svg" alt="沐仞科技标志"><img class="en" src="assets/wordmark-en.svg" alt="FATHOMPEAK"><img class="zh" src="assets/wordmark-zh.svg" alt="沐仞科技"></header>'];md=[];inlist=False;contact=False;current_section=''
    for b in items:
        t=b['text'];kind=b['kind']
        if inlist and kind!='li':chunks.append('</ul>');inlist=False
        if kind=='section':current_section=t
        if kind=='section' and t.startswith('七、'):chunks.append('<section class="contacts">');contact=True
        if kind=='title':
            chunks.append('<h1>'+html.escape(t)+'</h1><figure class="hero"><img src="assets/opening.png" alt="晨蓝版画山景，画面居中为从绿色电力到模型服务"></figure>');md+=['# '+t,'','![开篇视觉](assets/opening.png)',''];continue
        tag={'section':'h2','subheading':'h3','minor':'h4' if current_section.startswith('一、') else 'h3','li':'li'}.get(kind,'p')
        if kind=='li' and not inlist:chunks.append('<ul>');inlist=True
        anchor=f' id="section-{len([x for x in items[:items.index(b)+1] if x["kind"]=="section"])}"' if kind=='section' else ''
        chunks.append(f'<{tag}{anchor}>{inline(t)}</{tag}>')
        md+= [('## ' if kind=='section' else '### ' if kind=='subheading' else '#### ' if kind=='minor' else '- ' if kind=='li' else '')+t,'']
        if t=='沐仞科技围绕AI基础设施建设、算电协同调度和模型推理服务，开展三项核心业务。':
            chunks.append('<figure><img src="assets/business-stamps.png" alt="三枚复古邮票依次呈现词元工厂、协同调度和模型API"><figcaption>三项核心业务 · 概念插图</figcaption></figure>');md+=['![三项核心业务](assets/business-stamps.png)','']
    if inlist:chunks.append('</ul>')
    if contact:chunks.append('</section>')
    chunks.append('<figure class="closing"><img src="assets/closing.png" alt="沐仞科技合作联系卡：官网、商务邮箱与官方公众号二维码"></figure>');md+=['![合作联系卡](assets/closing.png)','']
    gallery=''.join(f'<div><img src="assets/{name}.png" alt="{label}" loading="lazy"><h3>{label}</h3><a href="assets/{name}.png" download>下载 PNG</a><a href="assets/{name}.svg" download>下载 SVG</a></div>' for name,label in [('opening','开篇 · 晨蓝版画'),('business-stamps','正文 · 三项业务邮票'),('closing','结尾 · 合作联系卡')])
    result=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{html.escape(TITLE)}</title><style>{CSS}</style></head><body><div class="toolbar"><a class="back" href="../../">项目与素材</a><button id="copy-rich" type="button">复制图文</button><button id="copy-text" type="button">复制纯文字</button><a href="{ZIP}" download>下载全文与配图</a><span class="status" id="copy-status" role="status" aria-live="polite"></span></div><main><article class="article" id="reading">'+''.join(chunks)+f'</article><section class="downloads"><h2>正文与配图下载</h2><p><a href="正文_排版稿_2026-10-22.md" download>下载 Markdown 正文</a>　<a href="正文_排版稿_2026-10-22.txt" download>下载纯文字</a></p><div class="asset-list">{gallery}</div><p class="note">配图为业务方向的概念表达。正文沿用提供的原稿，标题和联系信息已更新。</p></section></main><script>{JS}</script></body></html>'
    (OUT/'index.html').write_text(result)
    (OUT/'正文_排版稿_2026-10-22.md').write_text('\n'.join(md))
    (OUT/'正文_排版稿_2026-10-22.txt').write_text('\n\n'.join(('• ' if b['kind']=='li' else '')+b['text'] for b in items)+'\n')
    (OUT/'README.md').write_text('# 沐仞科技 · 业务与合作介绍\n\n'+TITLE+'\n\n打开 index.html 阅读、复制图文或下载素材。正文七章及顺序保留，仅更新标题并补充已在现有物料使用的官网与商务邮箱。\n\n- 正文为 DM Sans / Noto Sans SC；Logo 为已确认的 v31 路径字标。\n- assets/opening.png / .svg：1800 × 1013，晨蓝版画山景与居中文字。\n- assets/business-stamps.png / .svg：1800 × 900，三项业务邮票拼贴。\n- assets/closing.png / .svg：1800 × 850，合作联系卡与公众号二维码。\n- 图像底稿由内置 imagegen 生成；精确中文由原品牌字体转曲叠加，Logo 与二维码沿用批准的原文件。SVG 的图案、文字路径与图像分层，可在矢量工具中编辑。\n- generation-prompts.json 保存原始生图提示词。概念插图不代表已经建成的设施或部署规模。\n- 官网：https://www.fathompeak.cn/\n- 商务合作：fathompeak@163.com\n')
    dom=H.fromstring(result);body=dom.get_element_by_id('reading');actual=[e.text_content() for e in body.xpath('.//h1|.//h2|.//h3|.//h4|.//p|.//li')]
    assert len(actual)==len(items),(len(actual),len(items))
    for b,t in zip(items,actual):assert re.sub(r'\s','',b['text'])==re.sub(r'\s','',t),(b,t)
    assert len(body.xpath('.//h2'))==7
    assert '[待补充' not in body.text_content()
    for img in dom.xpath('//img'):assert (OUT/img.get('src')).is_file(),img.get('src')
    (OUT/'排版校验_2026-10-22.json').write_text(json.dumps({'title':TITLE,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sections':7,'content_blocks':len(items),'all_rendered_blocks_match':True,'allowed_changes':changes,'illustrations':3,'source_share_tokens_published':False},ensure_ascii=False,indent=2)+'\n')

def package():
    with zipfile.ZipFile(OUT/ZIP,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob('*')):
            if not f.is_file() or f.suffix=='.zip' or 'source' in f.relative_to(OUT).parts:continue
            if f.suffix in ['.html','.md','.json','.txt','.svg','.js']:
                text=f.read_text();assert 'docs.craft.do' not in text and '/Users/zixin' not in text
            z.write(f,f.relative_to(OUT))
    with zipfile.ZipFile(OUT/ZIP) as z:assert z.testzip() is None

def main():
    global FONT,SOURCE
    p=argparse.ArgumentParser();p.add_argument('--font',type=Path,required=True);p.add_argument('--source',type=Path,required=True);args=p.parse_args();FONT=args.font;SOURCE=args.source
    items,changes=blocks();fonts(items);cards();page(items,changes);package()
    logging.info('Business article built: %s sections, %s source-faithful blocks and three brand visuals.',7,len(items))

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(levelname)s: %(message)s');logging.getLogger('fontTools').setLevel(logging.WARNING)
    try:main()
    except Exception:logging.exception('Business article build failed');raise
