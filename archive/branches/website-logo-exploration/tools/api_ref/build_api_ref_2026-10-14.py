"""Compact the platform's OpenAPI spec (admin.fathompeak.cn/openapi/ai-model.json, fetched 2026-10-14)
into data/api-ref.json for the website's API reference page: groups -> operations with
params, body fields (refs resolved, two levels deep), responses and a request example."""
import json, re, sys
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding='utf-8'))
S = d['components']['schemas']
def res(s, seen=()):
    if not isinstance(s, dict): return {}
    if '$ref' in s:
        n = s['$ref'].split('/')[-1]
        if n in seen: return {'type': 'object', '_ref': n}
        r = dict(res(S.get(n, {}), seen + (n,))); r.setdefault('_ref', n); return r
    if 'allOf' in s:
        m = {'type': 'object', 'properties': {}, 'required': []}
        for x in s['allOf']:
            x = res(x, seen); m['properties'].update(x.get('properties', {})); m['required'] += x.get('required', [])
            if x.get('description') and not m.get('description'): m['description'] = x['description']
        return m
    if 'oneOf' in s or 'anyOf' in s:
        alts = [res(x, seen) for x in (s.get('oneOf') or s.get('anyOf'))]
        t = ' | '.join(sorted({tname(a) for a in alts}))
        r = dict(s); r['type'] = t; r.pop('oneOf', None); r.pop('anyOf', None); return r
    return s
def tname(s):
    s = res(s)
    t = s.get('type') or ('object' if 'properties' in s else '')
    if isinstance(t, list): t = ' | '.join(t)
    if t == 'array':
        it = res(s.get('items', {})); t = tname(it) + '[]'
    return t or 'any'
def fields(s, depth=0, maxd=2):
    s = res(s); rows = []
    if tname(s).endswith('[]'): s = res(s.get('items', {}))
    req = set(s.get('required', []))
    for k, v in (s.get('properties') or {}).items():
        v2 = res(v)
        row = {'n': k, 't': tname(v2), 'r': k in req, 'd': pub((v2.get('description') or v.get('description') or '').strip()), 'lv': depth}
        if v2.get('enum'): row['e'] = [str(x) for x in v2['enum']][:12]
        if v2.get('default') is not None: row['df'] = json.dumps(v2['default'], ensure_ascii=False)
        rows.append(row)
        inner = v2 if 'properties' in v2 else res(v2.get('items', {})) if row['t'].endswith('[]') else {}
        if depth + 1 < maxd and inner.get('properties'): rows += fields(inner, depth + 1, maxd)
    return rows
def example(s, depth=0):
    s = res(s)
    if 'example' in s: return s['example']
    if depth > 3: return None
    t = tname(s)
    if 'properties' in s:
        req = s.get('required') or list(s['properties'])[:2]
        return {k: example(s['properties'][k], depth + 1) for k in req if k in s['properties']}
    if t.endswith('[]'):
        e = example(s.get('items', {}), depth + 1); return [e] if e is not None else []
    if s.get('enum'): return s['enum'][0]
    return {'string': 'string', 'integer': 0, 'number': 0, 'boolean': False}.get(t.split(' | ')[0])

# Public edits (2026-10-14): drop admin-only channel configuration, fix enum values that the source
# mistranslated into Chinese, and point examples at the production domain.
EDITS=[
 ('- 渠道类型: Task Plugin（`task_plugin_key=fathom`）\n',''),
 ('### Sora 兼容渠道','### Sora 兼容格式'),
 ('当渠道绑定 Task Plugin `fathom` 且模型为 `minimax-h3-fl2va` 时','模型为 `minimax-h3-fl2va` 时'),
 ('（上游实际以 multipart 提交）',''),
 ('取决于上游渠道 Key 的权限','取决于上游服务的权限'),
 ('必须为`低，` 以进行限制较少的筛选或`自动`（默认值）','必须为 `low`（筛选较宽松）或 `auto`（默认值）'),
 ('必须是以下之一 `透明`、`不透明`或`自动`（默认值）。使用`自动`时','必须是 `transparent`、`opaque` 或 `auto`（默认值）之一。使用 `auto` 时'),
 ('如果`是透明`的','如果是 `transparent`'),
 ('`对于 gpt-image-1`，必须是','对于 `gpt-image-1`，必须是'),
 ('`或`自动`（默认值）之一，`对于 dall-e-2`，必须是 `256x256、``512x512` 或','或 `auto`（默认值）之一；对于 `dall-e-2`，必须是 `256x256`、`512x512` 或'),
 ('（纵向）或`自动`（默认值）之一，`对于 dall-e-2`，必须是 `256x256、``512x512` 或','（纵向）或 `auto`（默认值）之一；对于 `dall-e-2`，必须是 `256x256`、`512x512` 或'),
 ('wss://api.example.com','wss://api.fathompeak.cn'),
]
def pub(x):
    if not isinstance(x,str): return x
    for a,b in EDITS: x=x.replace(a,b)
    return x
tags = [t['name'] for t in d['tags']]
groups = []
for t in tags:
    if '/' in t: continue
    groups.append({'name': t, 'ops': []})
gi = {g['name']: g for g in groups}
for p, item in d['paths'].items():
    for m, op in item.items():
        if m not in ('get', 'post', 'put', 'delete', 'patch'): continue
        tag = (op.get('tags') or ['其他'])[0]; top = tag.split('/')[0]; sub = tag.split('/')[1] if '/' in tag else ''
        g = gi.get(top) or gi.setdefault(top, {'name': top, 'ops': []})
        if g not in groups: groups.append(g)
        o = {'id': re.sub(r'[^a-z0-9]+', '-', (m + '-' + p).lower()).strip('-'), 'm': m.upper(), 'p': p, 'sum': op.get('summary', ''), 'sub': sub,
             'desc': pub((op.get('description') or '').strip()), 'params': [], 'body': None, 'res': []}
        for prm in op.get('parameters', []):
            prm = res(prm)
            o['params'].append({'n': prm.get('name'), 'in': prm.get('in'), 'r': bool(prm.get('required')), 't': tname(prm.get('schema', {})), 'd': (prm.get('description') or '').strip()})
        rb = op.get('requestBody')
        if rb:
            ct, c = next(iter(rb.get('content', {}).items()), (None, {}))
            sch = c.get('schema', {})
            ex = c.get('example') or (next(iter(c.get('examples', {}).values()), {}) or {}).get('value') or example(sch)
            o['body'] = {'ct': ct, 'ref': res(sch).get('_ref', ''), 'f': fields(sch), 'ex': ex}
        for code, r in (op.get('responses') or {}).items():
            o['res'].append({'c': code, 'd': (r.get('description') or '').strip()})
        g['ops'].append(o)
groups = [g for g in groups if g['ops']]
json.dump({'title': d['info'].get('title'), 'version': d['info'].get('version'), 'groups': groups}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('groups', len(groups), 'ops', sum(len(g['ops']) for g in groups))
