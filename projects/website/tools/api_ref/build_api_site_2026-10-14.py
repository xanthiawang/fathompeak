"""Stage 2: turn api-ref.json (from build_api_ref_2026-10-14.py) into the data block embedded in the site's #api page.

- group order for developers (models -> chat -> ... -> moderations), zh / en group names
- display paths without the trailing slash the spec uses to tell duplicate paths apart
- unique op ids, CJK-Latin spacing in Chinese text
- usable request examples where the platform's example is a schema stub ("string", null, 0, [])
- en: zh -> en map from zh_strings.json + en_strings_2026-10-14.py, plus strings added here

Usage: python3 build_api_site_2026-10-14.py api-ref.json zh_strings.json en_strings_2026-10-14.py api-site.json
"""
import json, re, sys, runpy

src, zh_path, en_path, out = sys.argv[1:5]
ref = json.load(open(src))
zh = json.load(open(zh_path))
ens = runpy.run_path(en_path)
EN, EX_EN = ens['EN'], dict(ens['EX_EN'])
assert len(EN) == len(zh), (len(EN), len(zh))
CJK = re.compile(r'[㐀-鿿]')


def space(s):
    """Space between CJK and Latin/digits/backticks, as in the rest of the site."""
    if not s:
        return s
    s = re.sub(r'([㐀-鿿])([A-Za-z0-9`\[])', r'\1 \2', s)
    s = re.sub(r'([A-Za-z0-9`\)\]])([㐀-鿿])', r'\1 \2', s)
    return s


ENMAP = {}
for a, b in zip(zh, EN):
    ENMAP[a] = b
    ENMAP[space(a)] = b

ORDER = ['models', 'chat', 'completions', 'embeddings', 'rerank', 'images', 'videos', 'audio', 'realtime', 'moderations']
GROUP_ZH = {'models': '模型', 'chat': '聊天', 'completions': '补全', 'embeddings': '嵌入', 'rerank': '重排序', 'images': '图像',
            'videos': '视频', 'audio': '音频', 'realtime': '实时语音', 'moderations': '审查'}
GROUP_EN = {'models': 'Models', 'chat': 'Chat', 'completions': 'Completions', 'embeddings': 'Embeddings', 'rerank': 'Rerank',
            'images': 'Images', 'videos': 'Videos', 'audio': 'Audio', 'realtime': 'Realtime', 'moderations': 'Moderations'}
EXTRA_EN = {'实时语音': 'Realtime', '重排序': 'Rerank', '审查': 'Moderations', '补全': 'Completions', '嵌入': 'Embeddings'}

CHAT_MODEL = 'GLM-5.3-Flash'  # the model the site's quick start already uses
HELLO = '你好'
EX_EN.update({
    HELLO: 'Hello',
    '你好，有什么可以帮你？': 'Hello! How can I help?',
    '需要审查的文本': 'Text to check',
    '绿电算力': 'Green-power compute',
    '光伏电站旁的算力节点': 'A compute node next to a solar farm',
    '城市里的数据中心': 'A data center in the city',
    '你好，欢迎使用沐仞': 'Hello, welcome to FathomPeak',
    '一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书“义本生知人机同道善思新”，右书“通云赋智乾坤启数高志远”， 横批“智启通义”，字体飘逸，在中间挂着一幅中国风的画作，内容是岳阳楼。':
        'An elegant, formal pair of couplets hangs in a hall with quiet, classical Chinese furnishings and blue-and-white porcelain on the table. The left scroll reads “义本生知人机同道善思新”, the right reads “通云赋智乾坤启数高志远”, and the horizontal scroll reads “智启通义”, in flowing calligraphy. A Chinese-style painting of Yueyang Tower hangs in the middle.',
    '生成一张符合深度图的图像，遵循以下描述：一辆红色的破旧的自行车停在一条泥泞的小路上，背景是茂密的原始森林':
        'Generate an image that matches the depth map, following this description: a battered red bicycle parked on a muddy path, with dense old-growth forest behind it',
})

# Examples keyed by (method, display path, format sub-tag). json = request body; form = multipart fields;
# path = values for {path} params; query / headers = extra request parts; out = curl -o file.
FIX = {
    ('POST', '/v1/chat/completions', '原生OpenAI格式'): {'json': {'model': CHAT_MODEL, 'messages': [{'role': 'user', 'content': HELLO}]}},
    ('POST', '/v1/responses', '原生OpenAI格式'): {'json': {'model': CHAT_MODEL, 'input': HELLO}},
    ('POST', '/v1/responses/compact', '原生OpenAI格式'): {'json': {'model': CHAT_MODEL, 'input': [{'role': 'user', 'content': HELLO}, {'role': 'assistant', 'content': '你好，有什么可以帮你？'}]}},
    ('POST', '/v1/messages', ''): {'json': {'model': CHAT_MODEL, 'max_tokens': 1024, 'messages': [{'role': 'user', 'content': HELLO}]}, 'headers': {'anthropic-version': '2023-06-01'}},
    ('POST', '/v1beta/models/{model}:generateContent', ''): {'json': {'contents': [{'role': 'user', 'parts': [{'text': HELLO}]}]}, 'path': {'model': CHAT_MODEL}},
    ('POST', '/v1/completions', ''): {'json': {'model': CHAT_MODEL, 'prompt': HELLO, 'max_tokens': 256}},
    ('POST', '/v1/engines/{model}/embeddings', ''): {'json': {'model': 'text-embedding-ada-002', 'input': HELLO}, 'path': {'model': 'text-embedding-ada-002'}},
    ('POST', '/v1/embeddings', ''): {'json': {'model': 'text-embedding-ada-002', 'input': HELLO}},
    ('POST', '/v1/moderations', ''): {'json': {'input': '需要审查的文本'}},
    ('POST', '/v1/rerank', ''): {'json': {'model': 'rerank-english-v2.0', 'query': '绿电算力', 'documents': ['光伏电站旁的算力节点', '城市里的数据中心'], 'top_n': 1}},
    ('POST', '/v1beta/models/{model}:generateContent', '原生Gemini格式'): {'json': {'contents': [{'role': 'user', 'parts': [{'text': '一只猫在弹钢琴'}]}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '16:9'}}}},
    ('POST', '/v1/chat/completions', '原生Gemini格式'): {'json': {'model': 'MODEL_ID', 'stream': False, 'messages': [{'role': 'user', 'content': '一只猫在弹钢琴'}]}},
    ('POST', '/v1/images/generations', '原生OpenAI格式'): {'json': {'prompt': '一只猫在弹钢琴', 'n': 1, 'size': '1024x1024'}},
    ('POST', '/v1/images/edits', '原生OpenAI格式'): {'form': [['image', '@image.png'], ['prompt', '一只猫在弹钢琴']]},
    ('POST', '/v1/audio/transcriptions', '原生OpenAI格式'): {'form': [['file', '@audio.mp3'], ['model', 'whisper-1']]},
    ('POST', '/v1/audio/translations', '原生OpenAI格式'): {'form': [['file', '@audio.mp3'], ['model', 'whisper-1']]},
    ('POST', '/v1/audio/speech', '原生OpenAI格式'): {'json': {'model': 'tts-1', 'input': '你好，欢迎使用沐仞', 'voice': 'alloy'}, 'out': 'speech.mp3'},
    ('GET', '/v1/videos/{task_id}/content', 'Sora格式'): {'out': 'video.mp4'},
    ('POST', '/jimeng/', '即梦格式'): {'query': [['Action', 'CVSync2AsyncSubmitTask'], ['Version', '2022-08-31']]},
    ('GET', '/v1/realtime', ''): {'query': [['model', 'gpt-4o-realtime']]},
}

paths = [o['p'] for g in ref['groups'] for o in g['ops']]
groups, seen, used = [], set(), set()
by_key = {}
for g in ref['groups']:
    k = re.search(r'（(\w+)）', g['name']).group(1).lower()
    by_key[k] = g
for k in ORDER:
    g = by_key[k]
    ops = []
    for o in g['ops']:
        p = o['p']
        if p.endswith('/') and p.rstrip('/') in paths:
            p = p.rstrip('/')
        oid = 'ap-' + re.sub(r'[^a-z0-9]+', '-', (o['m'] + p).lower()).strip('-')
        n, base = 2, oid
        while oid in seen:
            oid = '%s-%d' % (base, n); n += 1
        seen.add(oid)
        fx = FIX.get((o['m'], p, o.get('sub') or '')) or {}
        body = o['body']
        ex = None
        if body:
            ex = body.get('ex')
            if isinstance(ex, str):
                t = ex.strip()
                try:
                    ex = json.loads(t)
                except ValueError:
                    ex = json.loads(t + '\n}')
        if 'json' in fx:
            ex = fx['json']
        if 'form' in fx:
            ex = None
        elif body and body['ct'].startswith('multipart') and isinstance(ex, dict):
            fx['form'] = [[a, ('@audio.mp3' if a == 'file' else v)] for a, v in ex.items() if v != '']
            ex = None
        op = {'id': oid, 'm': o['m'], 'p': p, 'sum': space(o['sum']), 'sub': space(o.get('sub') or ''), 'desc': space(o['desc'] or ''),
              'params': [dict(x, d=space(x['d'])) for x in o['params']],
              'body': ({'ct': body['ct'], 'f': [dict(f, d=space(f['d'])) for f in body['f']]} if body else None),
              'ex': ex, 'res': [dict(x, d=space(x['d'])) for x in o['res']]}
        for kk in ('form', 'path', 'query', 'headers', 'out'):
            if kk in fx:
                op[kk] = fx[kk]
        ops.append(op)
    groups.append({'k': k, 'zh': GROUP_ZH[k], 'en': GROUP_EN[k], 'ops': ops})

# every Chinese display string must have an English entry
need = set()
for g in groups:
    for o in g['ops']:
        for s in [o['sum'], o['sub'], o['desc']] + [x['d'] for x in o['params']] + [x['d'] for x in o['res']] + ([f['d'] for f in o['body']['f']] if o['body'] else []):
            if s and CJK.search(s):
                need.add(s)
ENMAP.update(EXTRA_EN)
missing = sorted(s for s in need if s not in ENMAP)
if missing:
    print('MISSING EN', len(missing))
    for s in missing:
        print('  ', repr(s[:120]))
    sys.exit(1)


def strings(x, acc):
    if isinstance(x, str):
        if CJK.search(x):
            acc.add(x)
    elif isinstance(x, dict):
        for v in x.values():
            strings(v, acc)
    elif isinstance(x, list):
        for v in x:
            strings(v, acc)


exs = set()
for g in groups:
    for o in g['ops']:
        strings(o['ex'], exs)
        strings(o.get('form'), exs)
miss_ex = sorted(s for s in exs if s not in EX_EN)
if miss_ex:
    print('MISSING EXAMPLE EN', miss_ex)
    sys.exit(1)

data = {'base': 'https://api.fathompeak.cn', 'groups': groups,
        'en': {s: ENMAP[s] for s in sorted(need)}, 'exen': {s: EX_EN[s] for s in sorted(exs)}}
txt = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
open(out, 'w').write(txt)
print('groups', len(groups), 'ops', sum(len(g['ops']) for g in groups), 'en', len(data['en']), 'exen', len(data['exen']), 'bytes', len(txt.encode()))
