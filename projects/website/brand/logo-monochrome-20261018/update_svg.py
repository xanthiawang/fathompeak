"""Update the approved vector lockups without changing the symbol or English.

Usage: python update_svg.py --source-svg-dir DIR --font NotoSerifCJKsc-Regular.otf
Requires fontTools and rsvg-convert. The earlier SVGs remain untouched.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import re
import json
import subprocess
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

NS='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',NS)
ET.register_namespace('inkscape',INK)

def node(tag,**attrs):
    return ET.Element(f'{{{NS}}}{tag}',{k:str(v) for k,v in attrs.items()})

def additions(font_path):
    font=TTFont(font_path)
    glyphs=font.getGlyphSet(); cmap=font.getBestCmap()
    bounds=BoundsPen(glyphs); paths=[]; advance=0
    for character in '科技':
        glyph=glyphs[cmap[ord(character)]]
        transform=(1,0,0,1,advance,0)
        pen=SVGPathPen(glyphs)
        glyph.draw(TransformPen(pen,transform))
        glyph.draw(TransformPen(bounds,transform))
        paths.append((character,pen.getCommands()))
        advance+=glyph.width+50
    x0,y0,x1,y1=bounds.bounds
    scale=47/(y1-y0)
    gap=6
    g=node('g',id='科技_宋体轮廓',transform=f'translate({104+gap-x0*scale:g} {y1*scale:g}) scale({scale:g} {-scale:g})')
    for character,d in paths:g.append(node('path',id=f'字形_{character}',d=d,fill='#000000'))
    return g,104+gap+(x1-x0)*scale

def fixed_geometry(root):
    paths=[]
    for g in root.iter(f'{{{NS}}}g'):
        if re.match(r'^0[1-6]_',g.get('id','')):
            paths.extend(dict(p.attrib) for p in g if p.tag==f'{{{NS}}}path')
    gradients=[ET.tostring(n,encoding='unicode') for n in root.findall('.//{'+NS+'}linearGradient')]
    english=[]
    for p in root.iter(f'{{{NS}}}path'):
        if p.get('id','').startswith(('英文科技字标-outline','英文两行字标-outline')):english.append(p.get('d'))
    return paths,gradients,english

def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-svg-dir',type=Path,required=True)
    parser.add_argument('--font',type=Path,required=True)
    args=parser.parse_args()
    out=Path(__file__).resolve().parent
    suffix,total_width=additions(args.font)
    mapping={
        '01_总版_主标圆形方形_可编辑.svg':'overview.svg',
        '02_主标组合_透明底.svg':'primary.svg',
        '03_圆形版本.svg':'circle.svg',
        '04_方形版本.svg':'square.svg',
        '05_独立峰面图形_透明底.svg':'symbol.svg',
    }
    records=[]
    for old,new in mapping.items():
        root=ET.parse(args.source_svg_dir/old).getroot()
        # Remove the alternate-type section from the board only.
        if new=='overview.svg':
            for item in list(root):
                if item.get('id','') in ['字标备选标题','备选科技字标','衬线FathomPeak']:
                    root.remove(item)
            for g in root:
                if g.get('id')=='版面分隔线':
                    for path in list(g):
                        if path.get('d')=='M972 789 V895':g.remove(path)
                if g.get('id')=='白色背景_可删除':g[0].set('height','780')
            root.set('height','780');root.set('viewBox','0 0 1605 780')
        before=fixed_geometry(root)
        changes=0
        for g in list(root):
            if g.tag!=f'{{{NS}}}g':continue
            if not any(c.get('id','').startswith('中文沐仞') for c in g):continue
            transform=g.get('transform','')
            match=re.fullmatch(r'translate\(([-.\d]+) ([-.\d]+)\) scale\(([-.\d]+)\)',transform)
            if not match:raise ValueError(f'Unexpected Chinese transform: {transform}')
            x,y,scale=map(float,match.groups())
            # Keep the existing two glyphs exactly. Append 科技 at the same
            # outline height and preserve the original horizontal center.
            center=x+104*scale/2
            g.set('transform',f'translate({center-total_width*scale/2:g} {y:g}) scale({scale:g})')
            g.set('aria-label','沐仞科技')
            g.set(f'{{{INK}}}label','中文_沐仞科技')
            g.append(deepcopy(suffix))
            changes+=1
        if fixed_geometry(root)!=before:raise AssertionError('Symbol or English unexpectedly changed')
        for tag in ['title','desc']:
            for n in root.findall(f'{{{NS}}}{tag}'):
                if n.text:n.text=n.text.replace('沐仞','沐仞科技')
        seen={}
        for n in root.iter():
            ident=n.get('id')
            if ident:
                seen[ident]=seen.get(ident,0)+1
                if seen[ident]>1:n.set('id',ident+f'-instance-{seen[ident]}')
        ET.indent(root,space='  ')
        target=out/new
        ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
        if root.findall('.//{'+NS+'}image'):raise AssertionError('Unexpected raster content')
        colors=re.findall(r'#[0-9a-fA-F]{6}\b',target.read_text())
        assert all(c[1:3]==c[3:5]==c[5:7] for c in colors)
        subprocess.run(['rsvg-convert','-o',str(target.with_suffix('.png')),str(target)],check=True,capture_output=True)
        records.append({'file':new,'chinese_lockups_updated':changes,'symbol_and_gradients_unchanged':True,'english_outlines_unchanged':True,'embedded_images':0})
    (out/'validation.json').write_text(json.dumps({'date':'2026-10-18','brand':'FathomPeak 沐仞科技','typeface_choice':'Selected technology wordmark only','checks':records},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(records,ensure_ascii=False))

if __name__=='__main__':
    try:run()
    except Exception as exc:raise SystemExit(f'Logo update failed: {exc}')
