#!/usr/bin/env python3
"""Export an editable, commit-pinned developer ZIP; never overwrite existing deliveries."""
import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/xanthiawang/fathompeak-site'
SITE = 'https://xanthiawang.github.io/fathompeak-site/'

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if git('status', '--porcelain').strip():
            raise RuntimeError('Commit or isolate working-tree changes before packaging.')
        commit = git('rev-parse', 'HEAD').decode().strip()
        now = datetime.now().astimezone()
        name = f'fathompeak-developer-{now:%Y-%m-%d}-{commit[:7]}'
        out = args.output.expanduser().resolve()
        if out == ROOT or ROOT in out.parents:
            raise RuntimeError('Choose an output folder outside the source checkout.')
        dest, archive = out / name, out / (name + '.zip')
        if dest.exists() or archive.exists():
            raise FileExistsError(f'Delivery already exists: {dest}')
        out.mkdir(parents=True, exist_ok=True)
        dest.mkdir()
        files = []
        with zipfile.ZipFile(io.BytesIO(git('archive', '--format=zip', 'HEAD'))) as source:
            for member in source.infolist():
                if member.is_dir():
                    continue
                target = dest / member.filename
                if not target.resolve().is_relative_to(dest):
                    raise RuntimeError(f'Unsafe archive path: {member.filename}')
                target.parent.mkdir(parents=True, exist_ok=True)
                data = source.read(member)
                target.write_bytes(data)
                files.append({'path':member.filename, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest(), 'origin':'git'})
        links = {'website':SITE+'#home', 'console_preview':SITE+'#console-preview', 'api_reference':SITE+'#api', 'source_repository':REPO, 'source_commit':REPO+'/tree/'+commit, 'online_editor':REPO+'/edit/main/index.html', 'release_downloads':REPO+'/releases'}
        data = (json.dumps(links, ensure_ascii=False, indent=2)+'\n').encode()
        (dest/'LINKS.json').write_bytes(data)
        files.append({'path':'LINKS.json','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'origin':'delivery metadata'})
        manifest = {'created_at':now.isoformat(), 'source_commit':commit, 'repository':REPO, 'scope':'Editable website and console FRONTEND, no application backend service', 'file_count_excluding_manifest':len(files), 'files':sorted(files,key=lambda x:x['path'])}
        (dest/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
            for path in sorted(dest.rglob('*')):
                if path.is_file():
                    bundle.write(path, str(Path(name)/path.relative_to(dest)))
        with zipfile.ZipFile(archive) as bundle:
            bad = bundle.testzip()
            if bad:
                raise RuntimeError(f'ZIP integrity failure: {bad}')
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        checksum = archive.with_suffix('.zip.sha256')
        checksum.write_text(f'{digest}  {archive.name}\n',encoding='utf-8')
        print(json.dumps({'folder':str(dest),'zip':str(archive),'checksum':str(checksum),'sha256':digest,'source_commit':commit,'zip_bytes':archive.stat().st_size},ensure_ascii=False,indent=2))
    except (OSError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f'Handoff export failed: {exc}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
