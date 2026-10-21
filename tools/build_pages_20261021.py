"""Publish active company projects without changing imported source snapshots."""
from pathlib import Path
import argparse, hashlib, html, json, logging, re, shutil

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://xanthiawang.github.io/fathompeak/'
PROJECTS = {'website': 'site', 'visual-materials': 'materials', 'developer-handoff': 'handoff'}
TEXT = {'.html', '.md', '.js', '.css', '.json', '.svg', '.txt', '.yml', '.yaml'}

def rewrite(text):
    for old, new in [('fathompeak-ui-kit','materials'),('fathompeak-handoff','handoff'),('fathompeak-site','site')]:
        for scheme in ['https','http']:
            text = text.replace(f'{scheme}://xanthiawang.github.io/{old}/', BASE+new+'/')
        repo = f'https://github.com/xanthiawang/{old}'
        prefix = next(k for k,v in PROJECTS.items() if v == new)
        for kind in ['blob','tree','edit']:
            text = text.replace(repo+f'/{kind}/main/', f'https://github.com/xanthiawang/fathompeak/{kind}/main/projects/{prefix}/')
        text = text.replace(repo+'/releases/latest', BASE+'archive/releases/')
        text = text.replace(repo+'/releases', BASE+'archive/releases/')
        text = text.replace(repo+'.git','https://github.com/xanthiawang/fathompeak.git')
        text = re.sub(re.escape(repo)+r'(?![A-Za-z0-9_/-])', 'https://github.com/xanthiawang/fathompeak/tree/main/projects/'+prefix, text)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'_site');args=p.parse_args()
    out=args.output.resolve()
    if out.exists():raise FileExistsError(f'Refusing to overwrite existing build output: {out}')
    out.mkdir(parents=True)
    changes=[]
    for source, destination in PROJECTS.items():
        shutil.copytree(ROOT/'projects'/source, out/destination, symlinks=False)
    shutil.copytree(ROOT/'archive/releases',out/'archive/releases')
    for file in sorted(out.rglob('*')):
        if not file.is_file() or file.suffix not in TEXT or file.stat().st_size>=3*1024*1024:continue
        before=file.read_bytes()
        try:after=rewrite(before.decode()).encode()
        except UnicodeDecodeError:continue
        if after!=before:
            file.write_bytes(after)
            changes.append({'path':str(file.relative_to(out)),'source_sha256':hashlib.sha256(before).hexdigest(),'published_sha256':hashlib.sha256(after).hexdigest()})
    shutil.copy2(ROOT/'index.html',out/'index.html')
    (out/'.nojekyll').touch()
    release_links=''.join(f'<li><a href="{html.escape(str(f.relative_to(out/"archive/releases")))}" download>{html.escape(f.name)}</a></li>' for f in sorted((out/'archive/releases').rglob('*.zip')))
    (out/'archive/releases/index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>沐仞科技 · 历史交付下载</title><h1>历史交付包</h1><p>历史发布原件，版本号保持不变。</p><ul>'+release_links+'</ul><p><a href="../../">返回统一入口</a></p></html>')
    # Imported project snapshots stay exact; record deployed link rewrites separately.
    (out/'migration-links.json').write_text(json.dumps({'base_url':BASE,'published_link_changes':changes},ensure_ascii=False,indent=2)+'\n')
    total=sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
    if total>1_000_000_000:raise RuntimeError(f'Pages output exceeds 1 GB: {total}')
    logging.info('Built %s bytes; rewrote links in %s files; source snapshots unchanged.',total,len(changes))

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,format='%(levelname)s: %(message)s')
    try:main()
    except Exception:logging.exception('Unified Pages build failed');raise
