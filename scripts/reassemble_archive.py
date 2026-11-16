"""Reassemble and verify downloaded Drive parts; does not extract or execute files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--parts-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    data=json.loads(args.manifest.read_text());whole=hashlib.sha256();total=0
    args.output.parent.mkdir(parents=True,exist_ok=True)
    handle=tempfile.NamedTemporaryFile(dir=args.output.parent,prefix='.reassembly-',delete=False);temporary=Path(handle.name)
    try:
        with handle:
            for part in data['parts']:
                name=part['file']
                if Path(name).name!=name or name in {'.','..'}:raise ValueError('Invalid part name')
                matches=list(args.parts_root.rglob(name))
                if len(matches)!=1 or matches[0].is_symlink():raise ValueError('Missing, duplicate or symlink part: '+name)
                source=matches[0]
                if source.stat().st_size!=part['bytes']:raise ValueError('Size mismatch: '+name)
                digest=hashlib.sha256()
                with source.open('rb') as inp:
                    for chunk in iter(lambda:inp.read(1024*1024),b''):
                        digest.update(chunk);whole.update(chunk);handle.write(chunk);total+=len(chunk)
                if digest.hexdigest()!=part['sha256']:raise ValueError('Checksum mismatch: '+name)
        if total!=data['archive_bytes'] or whole.hexdigest()!=data['archive_sha256']:raise ValueError('Whole archive checksum mismatch')
        # Exclusive destination creation preserves any concurrent user's output.
        os.link(temporary,args.output);temporary.unlink()
        print(json.dumps({'file':args.output.name,'bytes':total,'sha256':whole.hexdigest(),'verified':True}))
    finally:
        temporary.unlink(missing_ok=True)

if __name__=='__main__':main()
