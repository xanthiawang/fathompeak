from pathlib import Path
import base64, json, re
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "collateral"
log = print

def make_html():
    build=ROOT/'dist/client'
    document=(build/'index.html').read_text()
    js_match=re.search(r'<script\b[^>]*src="([^"]+)"[^>]*></script>',document)
    css_match=re.search(r'<link\b[^>]*href="([^"]+\.css)"[^>]*>',document)
    if not js_match or not css_match:raise ValueError('Expected the verified Vite entry script and stylesheet in dist/client/index.html')
    js=(build/js_match.group(1).lstrip('/')).read_text()
    css=(build/css_match.group(1).lstrip('/')).read_text()
    files={}
    resources=[(f'assets/{n}',mime) for n,mime in [('hero.webp','image/webp'),('layers.webp','image/webp'),('network.webp','image/webp'),('brandmark.svg','image/svg+xml'),('logo-system.png','image/png'),('favicon.svg','image/svg+xml'),('og.png','image/png')]]
    resources += [(f'fonts/{p.name}','font/woff2' if p.suffix=='.woff2' else 'font/woff') for p in (ROOT/'public/fonts').glob('*.woff*')]
    resources += [('downloads/fathompeak-a4.pdf','application/pdf'),('downloads/fathompeak-template.pptx','application/vnd.openxmlformats-officedocument.presentationml.presentation'),('design/tokens.json','application/json'),('design/figma-library-import.json','application/json')]
    for resource,mime in resources:
        file=ROOT/'public'/resource
        files['/'+resource]='data:'+mime+';base64,'+base64.b64encode(file.read_bytes()).decode()
    for key,value in files.items():
        css=css.replace(key,value)
        document=document.replace('"'+key+'"','"'+value+'"')
    document=document[:js_match.start()]+document[js_match.start():]
    document=re.sub(r'<script\b[^>]*src="[^"]+"[^>]*></script>',lambda _: '<script>window.__FATHOMPEAK_FILES__='+json.dumps(files,separators=(',',':'))+';</script><script type="module">'+js.replace('</script','<\\/script')+'</script>',document,count=1)
    document=re.sub(r'<link\b[^>]*href="[^"]+\.css"[^>]*>',lambda _: '<style>'+css+'</style>',document,count=1)
    if re.search(r'<script[^>]*\bsrc=|<link[^>]*rel="stylesheet"',document):raise ValueError('Standalone document still has an external script or stylesheet')
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'沐仞_品牌与产品原型_2026-10-12.html'
    target.write_text(document)
    (ROOT/'public/downloads/fathompeak-standalone.html').write_text(document)
    log(f'Self-contained HTML created with {len(files)} embedded resources: {target.name}')

if __name__ == "__main__":
    make_html()
