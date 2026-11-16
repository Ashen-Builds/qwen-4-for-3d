"""Prepare complete, deduplicated CCORE replay examples without training or executing HTML."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from collections import Counter
import pyarrow.parquet as pq
from transformers import AutoTokenizer
from inspect_generated_html import Scripts


def sha(text):return hashlib.sha256(text.encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--tokenizer',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--max-tokens',type=int,default=32768);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);(args.out/'provided-glbs').mkdir();tok=AutoTokenizer.from_pretrained(args.tokenizer,local_files_only=True,trust_remote_code=False)
    rejected=Counter();candidates=[];seen=set();heldout=re.compile(r'\b(babylon\w*|mesopotami\w*|iraqi?|market\w*|village\w*|canal\w*|town\w*)\b',re.I)
    # Only upstream train rows are considered. Author validation is never promoted to training.
    for f in sorted((args.source/'data').glob('train-*.parquet')):
        for batch in pq.ParquetFile(f).iter_batches(batch_size=32):
            for row in batch.to_pylist():
                messages=row['messages'];request=' '.join(m['content'] or '' for m in messages if m['role']=='user')
                if heldout.search(request+' '+row['title']):rejected['showcase_topic_exclusion']+=1;continue
                if [m['role'] for m in messages]!=['system','user','assistant']:rejected['role_format']+=1;continue
                final=messages[-1]['content'] or '';reason=messages[-1].get('reasoning_content') or ''
                if '</html>' not in final.lower():rejected['incomplete_html']+=1;continue
                digest=sha(re.sub(r'\s+',' ',final).strip());family=sha(row['domain']+'|'+re.sub(r'[^a-z0-9]','',row['title'].lower()))
                if digest in seen:rejected['exact_program_duplicate']+=1;continue
                seen.add(digest)
                ids=tok.apply_chat_template(messages,tokenize=True,return_dict=False)
                prefix=tok.apply_chat_template(messages[:-1],tokenize=True,add_generation_prompt=True,return_dict=False)
                if len(ids)>args.max_tokens:rejected['over_length_excluded_not_truncated']+=1;continue
                if not prefix or ids[:len(prefix)]!=prefix or len(prefix)>=len(ids):rejected['mask_prefix_mismatch']+=1;continue
                rendered=tok.apply_chat_template(messages,tokenize=False)
                if reason and reason[:120] not in rendered:rejected['reasoning_lost_by_template']+=1;continue
                parser=Scripts();parser.feed(final)
                if not parser.modules:rejected['no_javascript_module']+=1;continue
                with tempfile.TemporaryDirectory(prefix='astra-static-') as temp:
                    ok=True
                    for i,code in enumerate(parser.modules):
                        js=Path(temp)/f'{i}.mjs';js.write_text(code);result=subprocess.run(['node','--check',str(js)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                        if result.returncode:ok=False;break
                if not ok:rejected['module_syntax']+=1;continue
                candidates.append({'id':row['id'],'title':row['title'],'domain':row['domain'],'family':family,'program_sha256':digest,'tokens':len(ids),'masked_prefix_tokens':len(prefix),'messages':messages})
    # Inspect the actual publisher-exported GLB, without loading or executing its source.
    by_id={x['id']:x for x in candidates}
    for f in sorted((args.source/'meshes').glob('train-*.parquet')):
        for batch in pq.ParquetFile(f).iter_batches(batch_size=32):
            for row in batch.to_pylist():
                item=by_id.get(row['id'])
                if item is None:continue
                b=row['mesh']['bytes']
                try:
                    magic,version,length=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and length==len(b)
                    size=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+size]);assert len(doc.get('meshes',[]))>0
                    assert not any(x.get('uri') for x in doc.get('buffers',[])+doc.get('images',[]))
                    item['provided_glb_animations']=len(doc.get('animations',[]));item['provided_glb_bytes']=len(b);item['provided_glb_sha256']=hashlib.sha256(b).hexdigest()
                    (args.out/'provided-glbs'/f"{item['id']}.glb").write_bytes(b)
                except (AssertionError,ValueError,KeyError,struct.error):rejected['provided_glb_header_or_external_resource']+=1
    # Deterministic, subject-family disjoint continuation train/development split.
    # This is replay from a corpus already used by CCORE, never an independent final test.
    groups={'train':[],'valid':[]};families=set()
    for item in sorted(candidates,key=lambda x:(-x.get('provided_glb_animations',-1),sha(x['id']))):
        if 'provided_glb_animations' not in item:continue
        if item['family'] in families:rejected['subject_family_dedup']+=1;continue
        split='valid' if int(item['family'][:8],16)%10==0 else 'train'
        if len(groups[split])>=(64 if split=='valid' else 512):continue
        families.add(item['family']);groups[split].append(item)
    for split,items in groups.items():
        with (args.out/(split+'.jsonl')).open('w') as h:
            for item in items:h.write(json.dumps({'messages':item['messages']},ensure_ascii=False)+'\n')
    selected=[{k:v for k,v in x.items() if k!='messages'}|{'split':s} for s,items in groups.items() for x in items]
    (args.out/'PROVENANCE.json').write_text(json.dumps({'repo':'ccore/ThreeJS-3D-GLB-Assets','revision':args.source.name,'kind':'continuation-replay-not-novel-data','selected':selected},indent=2)+'\n')
    shutil_license=args.source/'LICENSE';(args.out/'LICENSE.source').write_bytes(shutil_license.read_bytes())
    report={'status':'pending-independent-GLB-validator','kind':'replay; no claim of novel model skill or independent evaluation','counts':{k:len(v) for k,v in groups.items()},'rejected':dict(rejected),'max_tokens':args.max_tokens,'truncation':False,'prompt_mask':'Pinned tokenizer full-token prefix exactly matches trainer prompt-only token prefix; reasoning retained','code_checks':'JavaScript module syntax only; HTML not executed; supplied GLBs are publisher outputs, not independent source re-execution','train_family_count':len({x['family'] for x in groups['train']}),'valid_family_count':len({x['family'] for x in groups['valid']}),'family_overlap':len({x['family'] for x in groups['train']}&{x['family'] for x in groups['valid']}),'selected_animated':sum(x.get('provided_glb_animations',0)>0 for x in groups['train'])}
    (args.out/'CURATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
