"""CPU-only derived full-program correction candidates; no runtime adoption.

Writes only explicit output/review directories. Source, repo and tokenizer
locations are CLI inputs. Never starts a server, runs HTML, a browser, MLX or a model.
"""
from pathlib import Path
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

SPECS = [
 ('asset-000168','hierarchy-export',r'exporter\.parse\(\s*assetScene,','exporter.parse(\n        assetRoot.children[0],','Export only assetRoot.children[0], the actual BottomPanel mesh, instead of the full DrawerCabinet hierarchy. Require the actual corrupt download to lose other named nodes/primitives or fail because its Drawer clip target is absent.'),
 ('asset-000348','flat-quaternion-values',r'("Rotor\.quaternion",\s*times,\s*)quaternionValues',r'\g<1>[quaternionValues]','Nested quaternion arrays must fail finite/value-size or serialized-track equivalence checks; existing samples must remain unchanged in the clean target.'),
 ('asset-000448','animation-binding',r'"ElevatorPlatform\.position"','"ElevatorPlatform_NotFound.position"','A nonexistent animation target must produce binding warnings, an absent channel, or a round-trip channel/binding mismatch.'),
 ('asset-000518','public-mixer-action',r'mixer\.clipAction\(swingClip\)','new THREE.AnimationAction(swingClip)','Passing only the clip to AnimationAction must fail at runtime; restore the existing public mixer.clipAction(swingClip) call. A two-argument private constructor was CPU-tested and rejected because it runs.'),
 ('asset-000622','serialize-existing-clips',r'animations:\s*\[idleClip\]','animations: []','The corrupt export must lose the existing Idle clip/channels even if its geometry renders.'),
 ('asset-003882','binary-export',r'binary:\s*true','binary: false','A JSON result wrapped as a .glb must fail the binary GLB header check; the clean export must be a real binary GLB.'),
]

def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()

def canon(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def digest(path):
    return {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active=False; self.modules=[]; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':
            self.active=dict(attrs).get('type')=='module';self.parts=[]
    def handle_data(self,data):
        if self.active:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.active:
            self.modules.append(''.join(self.parts));self.active=False

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('workspace','repo','tokenizer','source','out','serve-root'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--base-url',required=True,help='Existing loopback server URL for the new review subtree; no server is started')
    args=parser.parse_args()
    workspace=args.workspace.expanduser().resolve()
    def resolve(value):
        return value.expanduser().resolve() if value.is_absolute() else (workspace/value).resolve()
    REPO=resolve(args.repo)
    FROZEN=resolve(args.source)
    OUT=resolve(args.out)
    ROOT=OUT.parent
    SERVE=resolve(args.serve_root)
    BASE=args.base_url.rstrip('/')
    tokenizer_path=resolve(args.tokenizer)
    from urllib.parse import urlsplit
    parsed=urlsplit(BASE)
    if parsed.scheme!='http' or parsed.hostname not in {'localhost','127.0.0.1','::1'} or parsed.username or parsed.password:
        raise ValueError('base-url must be an existing unauthenticated loopback HTTP server')
    if OUT.is_relative_to(FROZEN) or FROZEN.is_relative_to(OUT) or SERVE.is_relative_to(FROZEN) or FROZEN.is_relative_to(SERVE) or OUT==SERVE:
        raise ValueError('Output/review paths must not overlap the frozen input')
    from transformers import AutoTokenizer
    assert not OUT.exists() and not SERVE.exists(),'Never overwrite a prepared dataset or review subtree'
    OUT.mkdir(parents=True);SERVE.mkdir(parents=True)
    manifest_path=FROZEN/'DATA_MANIFEST.json'
    original_manifest=digest(manifest_path)
    meta=sorted([x for x in json.loads((FROZEN/'ROW_PROVENANCE.json').read_text())['selected'] if x['kind']=='replay' and x['split']=='train'],key=lambda x:x['id'])
    rows=[json.loads(x) for x in (FROZEN/'replay/train.jsonl').read_text().splitlines()]
    by_id={m['id']:(index,m,row) for index,(m,row) in enumerate(zip(meta,rows),1)}
    probes=json.loads((REPO/'eval/sprint-probes-v1.json').read_text())
    aliases=[a for row in probes['final']+probes['development'] for a in row['exclude_training_aliases']]
    excluded=['babylon','mesopotami','iraq','market','village','canal','town']+aliases
    tokenizer=AutoTokenizer.from_pretrained(tokenizer_path,local_files_only=True,trust_remote_code=False)
    records=[];conversations=[];io_pairs=[]
    for identifier,family,pattern,replacement,intent in SPECS:
        line,meta,row=by_id[identifier]
        original=row['messages'][-1]['content']
        blocks=re.findall(r'```html\s*\n([\s\S]*?)\n```',original)
        assert len(blocks)==1 and blocks[0].strip().lower().endswith('</html>')
        clean=blocks[0]
        corrupt,count=re.subn(pattern,replacement,clean,count=1)
        assert count==1 and clean!=corrupt
        prompt='Correct the deliberately introduced API or serialization error in this complete standalone HTML. Preserve the existing geometry, materials, hierarchy and animation samples. Do not add assets or motion. Return the complete corrected HTML.\n\n```html\n'+corrupt+'\n```'
        target='```html\n'+clean+'\n```'
        messages=[{'role':'system','content':'You are a careful Three.js coding assistant. Repair complete standalone procedural HTML programs while preserving the supplied asset and its existing animation.'},{'role':'user','content':prompt},{'role':'assistant','content':target,'reasoning_content':''}]
        for text in [meta['title'],prompt,target]:
            compact=re.sub('[^a-z0-9]','',text.lower())
            assert not any(re.sub('[^a-z0-9]','',term.lower()) in compact for term in excluded),(identifier,'excluded alias')
        full=tokenizer.apply_chat_template(messages,tokenize=True,return_dict=False,enable_thinking=False)
        prefix=tokenizer.apply_chat_template(messages[:-1],tokenize=True,return_dict=False,add_generation_prompt=True,enable_thinking=False)
        assert full[:len(prefix)]==prefix and 0<len(prefix)<len(full)<=16384
        item=OUT/'examples'/identifier
        (OUT/'sources').mkdir(exist_ok=True)
        (OUT/'sources'/f'{identifier}.assistant.txt').write_text(original)
        node_checks={};served=[]
        for mode,code in [('clean',clean),('corrupt',corrupt)]:
            src=item/mode/'generated.html';src.parent.mkdir(parents=True);src.write_text(code)
            parser=Scripts();parser.feed(code);assert parser.modules
            with tempfile.TemporaryDirectory(dir=ROOT,prefix='syntax-') as temp:
                for i,module in enumerate(parser.modules):
                    module_path=Path(temp)/f'module-{i}.mjs';module_path.write_text(module)
                    checked=subprocess.run(['node','--check',str(module_path)],capture_output=True,text=True)
                    assert checked.returncode==0,(identifier,mode,checked.stderr)
            node_checks[mode]={'module_count':len(parser.modules),'syntax_pass':True,'source_executed':False}
            dest=SERVE/identifier/mode
            subprocess.run([sys.executable,str(Path(__file__).with_name('stage_generated_page.py')),'--run',str(src.parent),'--destination',str(dest)],check=True)
            # Review-only error display. It observes errors and never changes
            # scene code, export handlers, geometry, motion or model targets.
            review_label=json.dumps(f'{identifier} {mode}: review copy; errors shown below')
            debug='<script>(()=>{let notes=[];let box;const show=()=>{if(box)box.textContent='+review_label+'+"\\n"+notes.join("\\n")};window.addEventListener("error",e=>{notes.push("ERROR: "+e.message);show()});window.addEventListener("unhandledrejection",e=>{notes.push("REJECTION: "+String(e.reason));show()});document.addEventListener("DOMContentLoaded",()=>{box=document.createElement("pre");box.id="curriculumReviewStatus";box.style.cssText="position:fixed;right:6px;bottom:6px;z-index:2147483647;max-width:45vw;max-height:25vh;overflow:auto;padding:8px;background:#111c;color:#fff;font:11px monospace;pointer-events:none;white-space:pre-wrap";document.body.append(box);show()})})();</script>'
            generated=dest/'generated.html';staged=generated.read_text();staged=re.sub(r'<head\b[^>]*>',lambda m:m.group(0)+debug,staged,count=1,flags=re.I);generated.write_text(staged)
            adaptation=json.loads((dest/'adaptation.json').read_text());adaptation.update({'served_sha256':sha(staged),'review_error_overlay':True,'debug_ui_in_model_target':False,'source_executed':False});dump(dest/'adaptation.json',adaptation)
            url=f'{BASE}/{identifier}/{mode}/generated.html'
            readback=urllib.request.urlopen(url,timeout=5).read()
            assert sha(readback)==sha(generated.read_bytes())
            served.append({'mode':mode,'url':url,'source_html':str(src),'source_sha256':sha(code),'served_html':str(generated),'served_sha256':sha(readback),'adaptation':adaptation,'http_readback':True})
        buttons=re.findall(r'<button([^>]*)>([\s\S]*?)</button>',clean)
        export_buttons=[{'id':re.search(r'id=[\"\']([^\"\']+)',attrs).group(1),'label':re.sub('<[^>]+>','',label).strip()} for attrs,label in buttons if 'Export GLB' in label]
        assert len(export_buttons)==1
        downloads=sorted(set(re.findall(r'\.download\s*=\s*[\'\"]([^\'\"]+)',clean)))
        assert len(downloads)==1
        token_path=item/'TOKENS.json';dump(token_path,{'enable_thinking':False,'full_ids':full,'prefix_ids':prefix,'prompt_mask_end':len(prefix),'target_mask_end':len(full)})
        record={'id':identifier,'title':meta['title'],'correction_family':family,'status':'candidate-awaiting-source-runtime-export-and-negative-verification','original_split':'train','original_group_id':meta['group_id'],'source_jsonl':str(FROZEN/'replay/train.jsonl'),'source_line':line,'source_dataset':'ccore/ThreeJS-3D-GLB-Assets','source_revision':'276821245d5714b95571465569ed5b844ac6adc7','license':'MIT publisher declaration; retained notice','target_novelty':'Derived CCORE target; new controlled correction task, not independent asset/program generation supervision','source_assistant_sha256':sha(original),'clean_html_sha256':sha(clean),'corrupt_html_sha256':sha(corrupt),'geometry_and_motion_changes':'none in clean target; exact extracted original HTML','corruption':{'regex':pattern,'replacement':replacement,'replacements':count,'negative_check_intent':intent},'tokenization':{'enable_thinking':False,'local_files_only':True,'full_tokens':len(full),'prompt_tokens':len(prefix),'target_tokens':len(full)-len(prefix),'exact_prefix':True,'full_ids_sha256':sha(canon(full)),'prefix_ids_sha256':sha(canon(prefix)),'truncated':False,'cap':16384},'supplied_glb':meta['supplied_glb_evidence'],'source_validation_limits':'Publisher GLB validation is not source reexecution proof. Both clean and corrupt source must be executed and actual exported files checked before adoption.','node_checks':node_checks,'review':served,'export_button':export_buttons[0],'expected_download_name':downloads[0],'imported_source_versions':sorted(set(re.findall(r'three@([^/]+)',clean))),'staged_version':'0.160.0','debug_ui_outside_model_target':True}
        dump(item/'PAIR.json',record)
        records.append(record);conversations.append({'messages':messages});io_pairs.append({'id':identifier,'input':prompt,'output':target})
        links=''.join(f'<li><a href="{r["mode"]}/generated.html">{r["mode"]}</a></li>' for r in served)
        (SERVE/identifier/'index.html').write_text(f'<!doctype html><title>{html.escape(meta["title"])}</title><h1>{html.escape(meta["title"])}</h1><p>Candidate only. Open one scene at a time under the shared GPU guard.</p><ul>{links}</ul><p>Expected negative check: {html.escape(intent)}</p>')
    for name,data in [('train.jsonl',conversations),('pairs.jsonl',io_pairs)]:
        (OUT/name).write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in data))
    shutil.copyfile(FROZEN/'replay/LICENSE.source',OUT/'LICENSE.source')
    dump(OUT/'REVIEW_MANIFEST.json',{'status':'unqualified-candidates','source_manifest':original_manifest,'records':records,'no_validation_promotions':True,'current_data_and_configs_unchanged':True})
    dump(OUT/'QUALIFICATION_REQUIRED.json',{'adoption_allowed':False,'required_per_pair':['clean actual browser source execution without JS errors','actual clean binary GLB export and Khronos validation','actual exported geometry/hierarchy and clip/channel binding comparison','render/reimport and motion inspection at two times','controlled corrupt version fails intended invariant; reject ineffective negative','complete pair remains below16k and all artifacts frozen after qualification'],'all_six_clean_runtime_passed':False,'all_six_negative_checks_passed':False,'new_final_or_dev_family_used':False,'independent_full_program_target_claim':False})
    (OUT/'README.md').write_text('# Derived full-program correction candidates\n\nSix complete self-contained procedural HTML correction pairs. No GLB lookup inputs or new geometry/motion. These are new correction tasks over CCORE targets, not independent target programs. All source families were already training families. No current data, split or active configuration is changed.\n\ntrain.jsonl is a candidate only; QUALIFICATION_REQUIRED.json is deliberately false. The source and corrupted input are frozen; existing supplied GLBs are references, not source-execution proof. Review-only copies use localThree0.160,60FPS and an error display outside model targets. Rolling log originally imports0.164.1; that adaptation requires explicit qualification.\n')
    assert original_manifest==digest(manifest_path)
    files=[digest(path)|{'path':str(path.relative_to(OUT))} for path in sorted(OUT.rglob('*')) if path.is_file()]
    dump(OUT/'DATA_MANIFEST.json',{'schema':1,'status':'candidates-not-qualified-or-adopted','enable_thinking':False,'count':6,'source_manifest':original_manifest,'builder':digest(Path(__file__).resolve()),'max_full_tokens':max(x['tokenization']['full_tokens'] for x in records),'source_programs_executed':0,'browser_or_gpu_launches':0,'geometry_motion_authored':False,'files':files})
    print(json.dumps({'data':str(OUT),'manifest_sha256':sha((OUT/'DATA_MANIFEST.json').read_bytes()),'records':[{k:r[k] for k in ['id','title','tokenization','export_button','expected_download_name','review']} for r in records]},indent=2),flush=True)

if __name__=='__main__':main()
