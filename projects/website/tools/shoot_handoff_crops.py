"""Shoot the handoff-deck images from the current prototype and crop each to the exact
aspect ratio it is placed at in build_handoff_deck_2026-10-13.js (Keynote stretches images,
it ignores pptxgenjs `cover` sizing).

Usage: python3 shoot_handoff_crops_2026-10-13.py <out_dir>
Writes JPEGs plus aspects.json (footer height is measured, so its aspect is recorded).
"""
import json, os, sys, time, base64, io, subprocess, urllib.request, importlib.util
from PIL import Image

CDP = '/Users/zixin/programs/ai-skills/reference-site-prototype/scripts/cdp_client.py'
SRC = '/Users/zixin/Desktop/沐仞科技/site/index.html'  # the GitHub repo is the live source
out = os.path.abspath(sys.argv[1]); os.makedirs(out, exist_ok=True)
spec = importlib.util.spec_from_file_location('cdp', CDP); cdp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cdp)

site = SRC  # full HTML document; art/ and fonts/ resolve relative to it

port = 9531; prof = os.path.join(out, '.prof')
subprocess.run(['pkill', '-f', f'remote-debugging-port={port}']); subprocess.run(['rm', '-rf', prof])
proc = subprocess.Popen([cdp.CHROME, '--headless=new', f'--remote-debugging-port={port}', f'--user-data-dir={prof}', '--hide-scrollbars', '--window-size=1440,900', 'about:blank'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
aspects = {}

def ev(e):
    return ws.send('Runtime.evaluate', {'expression': e, 'returnByValue': True, 'awaitPromise': True}).get('result', {}).get('result', {}).get('value')
def vp(w, h, mob=False):
    ws.send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 2, 'mobile': mob})
def grab(clip=None):
    args = {'format': 'png'}
    if clip:
        args.update({'clip': dict(clip, scale=1), 'captureBeyondViewport': True})
    r = ws.send('Page.captureScreenshot', args)
    return Image.open(io.BytesIO(base64.b64decode(r['result']['data']))).convert('RGB')
def crop_aspect(im, aspect, anchor='center', top=0):
    W, H = im.size
    if W / H > aspect:  # too wide: trim sides
        w = int(H * aspect); x = (W - w) // 2; return im.crop((x, 0, x + w, H))
    h = int(W / aspect); y = top if anchor == 'top' else (H - h) // 2
    return im.crop((0, y, W, y + h))
def save(im, name, width, aspect=None):
    if aspect: im = crop_aspect(im, aspect)
    im = im.resize((width, round(width * im.size[1] / im.size[0])), Image.LANCZOS)
    im.save(os.path.join(out, name), quality=88); aspects[name] = im.size[0] / im.size[1]
def go(route, wait=2.2):
    ev(f"location.hash='#{route}'"); time.sleep(0.3)
    ev("document.querySelectorAll('.rv').forEach(function(e){e.classList.add('shown')})"); ev('scrollTo(0,0)'); time.sleep(wait)

try:
    for _ in range(50):
        try: urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=1); break
        except Exception: time.sleep(0.2)
    tab = json.loads(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/json/new?about:blank', method='PUT')).read())
    ws = cdp.WS(tab['webSocketDebuggerUrl']); ws.send('Page.enable'); ws.send('Runtime.enable')
    vp(1440, 900); ws.send('Page.navigate', {'url': 'file://' + site + '#home'}); time.sleep(5)
    ev('localStorage.clear()')

    go('home', 3)
    home = grab()                                            # 2880 x 1800
    save(home.crop((0, 12, 2880, 1800)), 'cover_sq.jpg', 1216, 5.7 / 5.625)            # cover, 5.7 x 5.625 in
    save(home, 'home_full.jpg', 1600, 4.6 / 2.875)           # slide 8, 4.6 x 2.875
    save(home.crop((0, 0, 2880, round(2880 / (3.6 / 1.16)))), 'mood_home.jpg', 1400)  # slide 3, 3.6 x 1.16
    for y, name in [(900, 'd_home_2.jpg'), (1800, 'd_home_3.jpg')]:
        ev(f'scrollTo(0,{y})'); time.sleep(1.4); save(grab(), name, 1400, 2.2 / 1.05)
    for route in ['enterprise', 'network']:
        go(route); im = grab()
        save(im.crop((0, 0, 2880, round(2880 / (3.6 / 1.16)))), f'mood_{route}.jpg', 1400)
    for route in ['models', 'enterprise', 'network', 'start']:
        go(route); im = grab(); save(im.crop((360, 0, 2520, round(2160 / (2.9 / 1.81)))), f'd_{route}.jpg', 1400)
    # footer, measured
    # nav pill on the products page, where the current-page state is visible
    go('models', 2)
    r = ev("(function(){var b=document.getElementById('pill').getBoundingClientRect();return [b.left,b.top,b.width,b.height]})()")
    pw = r[2] + 48; ph = pw / (6.0 / 0.65); cx = r[0] + r[2] / 2; cy = r[1] + r[3] / 2
    save(grab().crop((int((cx - pw / 2) * 2), int((cy - ph / 2) * 2), int((cx + pw / 2) * 2), int((cy + ph / 2) * 2))), 'pill.jpg', 1600)
    go('home', 1.5)
    # measure after the viewport is tall: the 100svh hero grows with the viewport and moves the footer
    vp(1440, 6000); time.sleep(1.5)
    f = ev("(function(){var b=document.querySelector('footer').getBoundingClientRect();return [b.top+scrollY,b.height]})()")
    foot = grab({'x': 140, 'y': f[0] + 20, 'width': 1160, 'height': f[1] - 20})
    save(foot, 'footer_only.jpg', 1800)
    vp(1440, 900)
    # mobile
    vp(390, 844, True); ws.send('Page.reload'); time.sleep(4); go('home', 2.5)
    save(grab(), 'm_home.jpg', 468, 1.3 / 2.81)
    ev("document.getElementById('plus').click()"); time.sleep(1.2)
    save(grab(), 'm_menu.jpg', 468, 1.3 / 2.81)
    json.dump(aspects, open(os.path.join(out, 'aspects.json'), 'w'), indent=1)
    print(json.dumps(aspects, indent=1))
finally:
    proc.terminate(); time.sleep(0.3); subprocess.run(['rm', '-rf', prof])
