"""Inspect data structure and duplicates without executing any embedded code."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics
import pyarrow.parquet as pq


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--datasets',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    report={'scope':'Static row/schema/duplicate inspection only; not execution or visual certification','sources':[]}
    for directory in sorted(args.datasets.iterdir()):
        if not directory.is_dir():continue
        revision=next((x for x in directory.iterdir() if x.is_dir()),None)
        if revision is None:continue
        item={'repo':directory.name.replace('--','/'),'revision':revision.name}
        if directory.name.startswith('ccore--'):
            ids={};code_hashes={};lengths=[];reason_lengths=[];roles={};html_closed=0
            for f in sorted((revision/'data').glob('*.parquet')):
                split='validation' if 'validation' in f.name else 'train';ids.setdefault(split,set());code_hashes.setdefault(split,set())
                pf=pq.ParquetFile(f)
                for batch in pf.iter_batches(batch_size=64):
                    for row in batch.to_pylist():
                        ids[split].add(row['id']);messages=row['messages'];key=','.join(m['role'] for m in messages);roles[key]=roles.get(key,0)+1
                        text='\n'.join(m.get('content') or '' for m in messages if m['role']=='assistant');reason='\n'.join(m.get('reasoning_content') or '' for m in messages if m['role']=='assistant')
                        lengths.append(len(text));reason_lengths.append(len(reason));html_closed+=int('</html>' in text.lower());norm=re.sub(r'\s+',' ',text).strip();code_hashes[split].add(hashlib.sha256(norm.encode()).hexdigest())
            item.update(unique_ids={k:len(v) for k,v in ids.items()},rows=len(lengths),role_sequences=roles,assistant_characters={'min':min(lengths),'median':statistics.median(lengths),'max':max(lengths)},reasoning_characters={'median':statistics.median(reason_lengths),'max':max(reason_lengths)},closed_html_rows=html_closed,exact_id_overlap=len(ids.get('train',set())&ids.get('validation',set())),normalized_response_overlap=len(code_hashes.get('train',set())&code_hashes.get('validation',set())),qualification='Whitespace-normalized response overlap only; variable-renaming/family overlap remains untested. Card claims rendered/validated; this audit has not independently rendered all examples.')
        elif directory.name.startswith('FreedomIntelligence'):
            rows=0;fields=set();duplicates=set();duplicate_rows=0
            with (revision/'BlendNet.jsonl').open() as h:
                for line in h:
                    if not line.strip():continue
                    row=json.loads(line);fields.update(row);rows+=1;digest=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest();duplicate_rows+=digest in duplicates;duplicates.add(digest)
            item.update(rows=rows,fields=sorted(fields),exact_duplicate_rows=duplicate_rows,role='optional Blender code; not direct Three.js demonstrations')
        elif directory.name.startswith('lamm-mit'):
            with (revision/'bioinspired3d_dataset_final.csv').open(newline='') as h:
                reader=csv.DictReader(h);fields=reader.fieldnames;rows=sum(1 for _ in reader)
            item.update(rows=rows,fields=fields,role='optional Blender code; not direct Three.js demonstrations')
        elif directory.name.startswith('codepawl'):
            tables=[pq.ParquetFile(f) for f in (revision/'data').glob('*.parquet')];item.update(rows=sum(x.metadata.num_rows for x in tables),fields=tables[0].schema_arrow.names,role='finished assets/reference only; not prompt-to-program training pairs')
        report['sources'].append(item)
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
