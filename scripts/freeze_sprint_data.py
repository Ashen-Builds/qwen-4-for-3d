"""Freeze statically checked replay and CPU-verified repair examples; never train."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from transformers import AutoTokenizer


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--repairs',type=Path,required=True);p.add_argument('--probes',type=Path,required=True);p.add_argument('--tokenizer',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);tok=AutoTokenizer.from_pretrained(args.tokenizer,local_files_only=True,trust_remote_code=False)
    probes=json.loads(args.probes.read_text());aliases=[a for row in probes['final']+probes['development'] for a in row['exclude_training_aliases']];pattern=re.compile('|'.join(re.escape(x) for x in aliases),re.I)
    source=json.loads((args.candidate/'PROVENANCE.json').read_text());checks=json.loads((args.candidate/'GLB_VALIDATION.json').read_text());good={x['id'] for x in checks['rows'] if x['errors']==0};selected=[];reports={}
    for kind,root,cap in [('replay',args.candidate,32768),('repairs',args.repairs,4096)]:
        directory=args.out/kind;directory.mkdir();counts={};lengths=[];omitted=0
        for split in ['train','valid']:
            rows=[json.loads(x) for x in (root/(split+'.jsonl')).read_text().splitlines() if x.strip()];meta=[x for x in source['selected'] if x['split']==split] if kind=='replay' else [None]*len(rows)
            assert len(rows)==len(meta)
            keep=[]
            for row,item in zip(rows,meta):
                request=' '.join(m.get('content') or '' for m in row['messages'] if m['role']=='user')
                if pattern.search(request+' '+(item['title'] if item else '')):omitted+=1;continue
                if item and item['id'] not in good:omitted+=1;continue
                ids=tok.apply_chat_template(row['messages'],tokenize=True,return_dict=False);prefix=tok.apply_chat_template(row['messages'][:-1],tokenize=True,return_dict=False,add_generation_prompt=True)
                assert len(ids)<=cap and ids[:len(prefix)]==prefix and 0<len(prefix)<len(ids),'Length/mask failure'
                keep.append(row);lengths.append(len(ids))
                if item:selected.append(item)
            (directory/(split+'.jsonl')).write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in keep));counts[split]=len(keep)
        assert counts['train']>0 and counts['valid']>0
        shutil.copyfile(root/'LICENSE.source',directory/'LICENSE.source')
        reports[kind]={'counts':counts,'min_tokens':min(lengths),'max_tokens':max(lengths),'cap':cap,'truncation':False,'exact_mask_prefix':True,'heldout_alias_rows_removed':omitted}
    trainfamilies={x['family'] for x in selected if x['split']=='train'};validfamilies={x['family'] for x in selected if x['split']=='valid'};assert not trainfamilies&validfamilies
    manifest={'schema':1,'status':'prepared-for-authorized-qualification; not trained','source_revision':source['revision'],'datasets':reports,'family_overlap':0,'test_policy':'20 final families plus four development families and Babylon excluded by declared aliases; upstream pretraining absence is unknown','provided_glbs':'All retained replay targets have independently validator-passing supplied exports; source HTML not re-executed','repair_checks':json.loads((args.repairs/'CURRICULUM_REPORT.json').read_text()),'files':[]}
    for f in sorted(args.out.rglob('*')):
        if f.is_file():manifest['files'].append({'path':str(f.relative_to(args.out)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    (args.out/'DATA_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');(args.out/'REPLAY_PROVENANCE.json').write_text(json.dumps({'selected':selected},indent=2)+'\n');print(json.dumps(reports))

if __name__=='__main__':main()
