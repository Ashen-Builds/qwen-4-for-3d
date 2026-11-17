"""CPU-only readiness checks. This command cannot launch a model or training."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import yaml


def inspect(repo):
    cfg=yaml.safe_load((repo/'configs/lora-qualification.yaml').read_text());work=repo.parent/'work/sprint-prep';checks={}
    phase_configs=[yaml.safe_load((repo/'configs'/name).read_text()) for name in ['lora-qualification.yaml','lora-length-qualification.yaml','lora-main-draft.yaml']]
    checks['all_phase_configs_safe']=all(c['train'] is False and c['test'] is False and c['fine_tune_type']=='lora' and c['num_layers']==1 and c['trust_remote_code'] is False and c.get('report_to') is None and c['model']==cfg['model'] and c['lora_parameters']==cfg['lora_parameters'] for c in phase_configs)
    checks['frozen_prefix_scope']=all(c.get('frozen_prefix_inference') is True and c['grad_checkpoint'] is False and c['num_layers']==1 for c in phase_configs)
    checks['training_disabled']=cfg['train'] is False and cfg['test'] is False
    checks['remote_code_disabled']=cfg['trust_remote_code'] is False
    checks['external_reporting_disabled']=cfg.get('report_to') is None
    checks['model_present']=(repo/cfg['model']/'config.json').is_file()
    audit_path=(repo/cfg['adapter_setup_audit']).resolve() if cfg.get('adapter_setup_audit') else work/'adapter-setup-audit.json'
    audit=json.loads(audit_path.read_text())
    rank=cfg['lora_parameters']['rank']
    tensors=audit['trainable_tensors']
    rank_matches=bool(tensors) and all(t['shape'][1 if t['name'].endswith('lora_a') else 0]==rank for t in tensors)
    checks['adapter_shape_check']=audit['trained_steps']==0 and audit['final_layer_full_attention'] and audit['adapted_last_layers']==cfg['num_layers'] and audit['trainable_parameters']==59904*rank and len(tensors)==14 and rank_matches
    checks['all_phase_adapter_audits_match']=all(c.get('adapter_setup_audit')==cfg.get('adapter_setup_audit') for c in phase_configs)
    data=(repo/cfg['data']).resolve().parent;manifest=json.loads((data/'DATA_MANIFEST.json').read_text());checks['data_hashes']=all((data/f['path']).stat().st_size==f['bytes'] and hashlib.sha256((data/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in manifest['files'])
    checks['complete_targets']=all(not row['truncation'] for row in manifest['datasets'].values())
    checks['masks_and_lengths']=manifest['datasets']['repairs']['exact_mask_prefix'] and manifest['datasets']['repairs']['max_tokens']<=cfg['max_seq_length']
    checks['family_split']=manifest['family_overlap']==0
    checks['all_phase_data_bound_to_manifest']=all((repo/c['data']).resolve().parent==data for c in phase_configs)
    checks['mode_matches_data']=bool(cfg.get('response_only_training'))==bool(manifest.get('response_only_training',False) or manifest.get('enable_thinking') is False)
    tokenizer=json.loads((work/'tokenizer-equivalence.json').read_text())
    checks['actual_training_tokenizer_qualified']=all(tokenizer['checks'].values()) and tokenizer['actual_training_tokenizer_prefix_and_ids_match']
    probes=json.loads((repo/'eval/sprint-probes-v1.json').read_text());checks['frozen_probes']=len(probes['final'])==20 and len(probes['development'])==4 and probes['seeds']==[42,1234]
    versions={name:importlib.metadata.version(name) for name in ['mlx','mlx-lm','transformers','huggingface-hub']}
    checks['runtime_available']=versions['mlx-lm']=='0.32.2'
    result={'status':'ready-for-authorized-qualification' if all(checks.values()) else 'preparation-check-failed','training_started':False,'checks':checks,'versions':versions,'datasets':manifest['datasets'],'remaining_live_gate':['actual backward completion; finite losses and adapter weights','representative-length memory and step time','save/reload and restored adapter effect','raw full-scene export and visual regression evaluation'],'full_unattended_48h_qualified':False,'note':'All these checks are preparation. Do not turn a passing dry run into a claim of training or output improvement.'}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path.cwd());p.add_argument('--out',type=Path);args=p.parse_args();r=inspect(args.repo.resolve())
    if args.out:args.out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2));raise SystemExit(0 if all(r['checks'].values()) else 1)

if __name__=='__main__':main()
