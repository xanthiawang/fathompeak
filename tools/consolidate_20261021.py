"""Import public repository snapshots without merging historical Git graphs."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,logging,os,re,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ('fathompeak-site','source-site','main','projects/website','active'),
 ('fathompeak-ui-kit','source-ui-kit','main','projects/visual-materials','active'),
 ('fathompeak-handoff','source-handoff','main','projects/developer-handoff','active'),
 ('fathompeak-discarded-draft','source-discarded','main','archive/early-website','historical'),
 ('fathompeak-energy-draft','source-energy','main','archive/energy-draft','historical'),
 ('fathompeak-pine-draft','source-pine','main','archive/pine-draft','historical'),
 ('fathompeak-purple-draft','source-purple','main','archive/purple-draft','historical'),
 ('fathompeak-site','source-site','codex/logo-svg-monochrome-20261018','archive/branches/website-logo-exploration','historical-branch'),
]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def run(*args):subprocess.run(list(args),cwd=ROOT,check=True)
def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def tree(sha):
 result=[]
 for raw in git('ls-tree','-r','-z','--long',sha).split(b'\0'):
  if not raw:continue
  meta,path=raw.split(b'\t',1);mode,kind,oid,size=meta.split()
  if kind!=b'blob':raise RuntimeError('Nested Git object requires explicit handling: '+path.decode())
  if int(size)>=100*1024*1024:raise RuntimeError('File exceeds GitHub single-file limit: '+path.decode())
  result.append({'path':path.decode(),'mode':mode.decode(),'git_blob_sha':oid.decode(),'bytes':int(size)})
 return result
def import_snapshots():
 if git('status','--porcelain').strip():raise RuntimeError('Commit the local checkpoint before importing snapshots.')
 repositories=[];allfiles=[]
 for repo,remote,branch,prefix,role in SOURCES:
  sha=git('rev-parse','refs/remotes/'+remote+'/'+branch).decode().strip()
  source_tree=git('rev-parse',sha+'^{tree}').decode().strip()
  files=tree(sha)
  if (ROOT/prefix).exists():raise RuntimeError('Refusing to overwrite an existing project folder: '+prefix)
  run('git','read-tree','--prefix='+prefix+'/','-u',sha+'^{tree}')
  run('git','commit','-m','Import '+repo+' '+branch+' snapshot at '+sha[:12])
  actual=git('rev-parse','HEAD:'+prefix).decode().strip()
  if actual!=source_tree:raise RuntimeError('Imported Git tree differs from source: '+prefix)
  repositories.append({'repository':'xanthiawang/'+repo,'url':'https://github.com/xanthiawang/'+repo,'visibility':'public','branch':branch,'source_commit':sha,'source_tree':source_tree,'folder':prefix,'role':role,'file_count':len(files),'bytes':sum(x['bytes'] for x in files),'source_commit_url':'https://github.com/xanthiawang/'+repo+'/tree/'+sha})
  allfiles.extend({'folder':prefix,**x} for x in files)
 now=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
 write_json(ROOT/'metadata/source-repositories.json',{'recorded_at':now,'method':'Public GitHub branch snapshots; original repository histories and websites retained.','sources':repositories})
 write_json(ROOT/'metadata/source-files.json',allfiles)
 verify()
def credential_findings():
 findings=[]
 patterns=[re.compile(r'(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{30,}'),re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'docs\.craft\.do/editor/[^\s"<>]{0,500}[?&]s=[A-Za-z0-9]{20,}')]
 extensions={'.txt','.md','.html','.json','.py','.js','.ts','.yml','.yaml','.toml','.env','.ini','.sh','.css'}
 for folder in ['projects','archive']:
  for path in (ROOT/folder).rglob('*'):
   if not path.is_file():continue
   if path.name in {'.env','auth.json','credentials.json','secrets.json'}:findings.append(str(path.relative_to(ROOT)))
   if path.suffix in extensions and path.stat().st_size<3*1024*1024:
    content=path.read_text(errors='replace')
    if any(pattern.search(content) for pattern in patterns):findings.append(str(path.relative_to(ROOT)))
 return sorted(set(findings))
def release_records():
 records=[]
 for checksum in sorted((ROOT/'archive/releases').glob('*/*.sha256')):
  digest=checksum.read_text().split()[0]
  file=checksum.with_suffix('')
  actual=hashlib.sha256(file.read_bytes()).hexdigest()
  if actual!=digest:raise RuntimeError('Release checksum mismatch: '+str(file))
  with zipfile.ZipFile(file) as z:
   if z.testzip() is not None:raise RuntimeError('Release archive is corrupt: '+str(file))
  records.append({'tag':checksum.parent.name,'file':str(file.relative_to(ROOT)),'bytes':file.stat().st_size,'sha256':actual,'source_url':'https://github.com/xanthiawang/fathompeak-site/releases/tag/'+checksum.parent.name})
 return records
def verify():
 sources=json.loads((ROOT/'metadata/source-repositories.json').read_text())['sources']
 files=json.loads((ROOT/'metadata/source-files.json').read_text())
 for item in files:
  path=ROOT/item['folder']/item['path']
  data=os.readlink(path).encode() if item['mode']=='120000' else path.read_bytes()
  blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if blob!=item['git_blob_sha'] or len(data)!=item['bytes']:raise RuntimeError('File content changed: '+str(path))
  if item['mode']=='100755' and not path.stat().st_mode&0o111:raise RuntimeError('Executable permission missing: '+str(path))
 for source in sources:
  expected={x['path'] for x in files if x['folder']==source['folder']}
  actual={str(x.relative_to(ROOT/source['folder'])) for x in (ROOT/source['folder']).rglob('*') if x.is_file() or x.is_symlink()}
  if expected!=actual:raise RuntimeError('Missing or unexpected files in '+source['folder'])
 findings=credential_findings()
 releases=release_records()
 record={'verified_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),'repositories':len({x['repository'] for x in sources}),'branch_snapshots':len(sources),'source_files':len(files),'source_bytes':sum(x['bytes'] for x in files),'content_and_permissions':'matched source Git blob IDs and executable modes','release_assets':releases,'potential_sensitive_files':findings,'original_repositories_modified':False,'existing_website_urls_changed':False,'pages_enabled_for_consolidated_repo':False}
 write_json(ROOT/'metadata/verification.json',record)
 if findings:raise RuntimeError('Review potential sensitive files before publishing: '+', '.join(findings))
 logging.info('Verified %s repositories, %s branch snapshots, %s source files and %s release archives.',record['repositories'],record['branch_snapshots'],record['source_files'],len(releases))
if __name__=='__main__':
 logging.basicConfig(level=logging.INFO,format='%(levelname)s: %(message)s')
 try:
  if '--import' in sys.argv:import_snapshots()
  elif '--verify' in sys.argv:verify()
  else:raise RuntimeError('Choose --import for first-time intake or --verify for integrity checks.')
 except Exception:logging.exception('Company repository consolidation failed');raise
