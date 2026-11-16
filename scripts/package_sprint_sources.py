"""Package exact task sources and split below the connector's 100 MiB transfer cap."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    roots=[
        ('ccore-original-checkpoint',args.work/'models/ccore--Qwen3.5-4B-GLB-3D-Coder','model-backup'),
        ('ccore-scenes-dataset',args.work/'datasets/ccore--ThreeJS-3D-Scenes','supplementary-code'),
        ('3dcodeverse-research-only',args.work/'datasets/3dcodeverse--3dcodeverse-2m','noncommercial-quarantine'),
    ]
    for name,root,role in roots:
        archive=args.out/(name+'.zip')
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
            for f in sorted(root.rglob('*')):
                if f.is_file() and '.cache' not in f.parts and not f.is_symlink():z.write(f,str(f.relative_to(root.parent)))
        print(json.dumps({'archive':archive.name,'bytes':archive.stat().st_size,'role':role}),flush=True)
    manifest=[]
    for archive in sorted(args.out.glob('*.zip')):
        target=args.out/archive.stem;target.mkdir(exist_ok=True)
        whole=hashlib.sha256();parts=[]
        with archive.open('rb') as h:
            i=1
            while data:=h.read(96*1024*1024):
                whole.update(data);part=target/f'{archive.name}.part{i:04d}';part.write_bytes(data)
                parts.append({'file':part.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});i+=1
        item={'package':archive.stem,'archive_file':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':whole.hexdigest(),'parts':parts}
        (target/'CHECKSUMS.json').write_text(json.dumps(item,indent=2)+'\n');manifest.append(item)
        print(json.dumps({'package':archive.stem,'parts':len(parts),'bytes':archive.stat().st_size}),flush=True)
    (args.out/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
