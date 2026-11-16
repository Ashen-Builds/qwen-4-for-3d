"""Acquire pinned public sprint sources, verify digests; never execute data or train."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
from huggingface_hub import HfApi, hf_hub_download

SOURCES = [
    ('ccore/ThreeJS-3D-GLB-Assets', '276821245d5714b95571465569ed5b844ac6adc7', 'core-replay', 'MIT declaration'),
    ('FreedomIntelligence/BlendNet', '11a779c7723af9bacbed371fccdc643ea20be446', 'optional-blender', 'Apache-2.0 declaration'),
    ('lamm-mit/Bioinspired3D', '8901dd3fa5f7218bc453d17f65a6faf7bd15ae12', 'optional-blender', 'MIT declaration'),
    ('codepawl/pixel-atlas-glb', '98046fef34d7443439ff292e246701b5593eadfa', 'asset-reference-only', 'CC0 declaration; upstream attribution retained'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    api = HfApi(token=False)
    plans = []
    for repo, revision, role, license_name in SOURCES:
        info = api.dataset_info(repo, revision=revision, files_metadata=True)
        files = []
        for f in info.siblings:
            if repo == 'codepawl/pixel-atlas-glb' and not (f.rfilename.startswith('data/') or '/' not in f.rfilename):
                continue  # parquet already contains assets; avoid duplicate engine/web/collision copies
            files.append({'path':f.rfilename, 'bytes':f.size, 'upstream_sha256':f.lfs.sha256 if f.lfs else None, 'git_blob':f.blob_id})
        plans.append({'repo':repo, 'revision':revision, 'role':role, 'license':license_name, 'files':files})
    total = sum(f['bytes'] for s in plans for f in s['files'])
    print(json.dumps({'selected_bytes':total,'sources':len(plans)}),flush=True)
    if not args.download:
        return
    if (Path.home()/'.cache/gpu-slot/STREAMING').exists():
        raise RuntimeError('Streaming guard active; defer bulk download')
    args.destination.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(args.destination).free < total + 20*1024**3:
        raise RuntimeError('Need payload space plus 20 GiB reserve')
    for plan in plans:
        directory=args.destination/plan['repo'].replace('/','--')/plan['revision']
        def acquire(f):
            path=Path(hf_hub_download(plan['repo'],f['path'],repo_type='dataset',revision=plan['revision'],local_dir=directory,token=False))
            assert path.stat().st_size==f['bytes'], f['path']
            sha=hashlib.sha256();blob=hashlib.sha1(f"blob {f['bytes']}\0".encode())
            with path.open('rb') as h:
                for chunk in iter(lambda:h.read(1024*1024),b''):sha.update(chunk);blob.update(chunk)
            if f['upstream_sha256']:assert sha.hexdigest()==f['upstream_sha256'],f['path']
            else:assert blob.hexdigest()==f['git_blob'],f['path']
            return {**f,'sha256':sha.hexdigest(),'verified':True}
        with ThreadPoolExecutor(max_workers=4) as pool:plan['files']=list(pool.map(acquire,plan['files']))
        (directory/'COPY_MANIFEST.json').write_text(json.dumps(plan,indent=2)+'\n')
        print(json.dumps({'repo':plan['repo'],'files':len(plan['files']),'bytes':sum(f['bytes'] for f in plan['files']),'verified':True}),flush=True)
    (args.destination/'SPRINT_SOURCE_MANIFEST.json').write_text(json.dumps(plans,indent=2)+'\n')

if __name__=='__main__':
    main()
