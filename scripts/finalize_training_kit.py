"""Create explicit replay/repair sampling and a complete-target length probe. No training."""
import argparse
import hashlib
import json
from pathlib import Path


def rows(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def write(path,data):path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in data))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);args=p.parse_args();root=args.directory
    if (root/'mixture').exists():raise FileExistsError('Frozen kit already finalized')
    replay={s:rows(root/'replay'/(s+'.jsonl')) for s in ['train','valid']};repairs={s:rows(root/'repairs'/(s+'.jsonl')) for s in ['train','valid']}
    mix=root/'mixture';mix.mkdir();write(mix/'train.jsonl',replay['train']+repairs['train']*8);write(mix/'valid.jsonl',replay['valid']+repairs['valid'])
    prov=json.loads((root/'REPLAY_PROVENANCE.json').read_text())['selected'];trainmeta=[x for x in prov if x['split']=='train'];order=sorted(range(len(trainmeta)),key=lambda i:trainmeta[i]['tokens']);chosen=[order[0],order[len(order)//2],order[-1]]
    long=root/'length-probe';long.mkdir();write(long/'train.jsonl',[replay['train'][i] for i in chosen]);write(long/'valid.jsonl',[replay['valid'][0]])
    report={'mixing':'Replay rows once; repair rows repeated eight times as explicit example weighting. Repetitions are not independent programs. Provisional mixture, not an optimized recipe.','mixture_counts':{'train':len(replay['train'])+8*len(repairs['train']),'valid':len(replay['valid'])+len(repairs['valid'])},'unique_conversations':{'train':len(replay['train'])+len(repairs['train']),'valid':len(replay['valid'])+len(repairs['valid'])},'repair_families':{'train':8,'valid':2},'length_probe_tokens':[trainmeta[i]['tokens'] for i in chosen],'policy':'Qualification and measured length cost precede any main segment; no truncation; stop on regressions. No training performed.'}
    (root/'MIXTURE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    p=root/'DATA_MANIFEST.json';d=json.loads(p.read_text());d['mixture']=report;d['files']=[{'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(root.rglob('*')) if f.is_file() and f.name!='DATA_MANIFEST.json'];p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
