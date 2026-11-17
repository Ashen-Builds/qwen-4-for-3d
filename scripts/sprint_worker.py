"""Trusted live worker. Never invoked by controller dry tests. No imports until authorized."""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import types


def train(repo, job, directory):
    import yaml
    import numpy as np
    import mlx.core as mx
    mx.set_memory_limit(160*1024**3)  # MLX advisory limit; parent enforces RSS/free-memory guards
    mx.set_cache_limit(2*1024**3)
    from mlx_lm import load
    from mlx_lm.lora import CONFIG_DEFAULTS, train_model
    from mlx_lm.tuner.datasets import load_dataset
    from mlx_lm.tuner.callbacks import TrainingCallback
    name={'short':'lora-qualification.yaml','length':'lora-length-qualification.yaml','segment':'lora-main-draft.yaml'}[job['kind']]
    cfg={**copy.deepcopy(CONFIG_DEFAULTS),**yaml.safe_load((repo/'configs'/name).read_text())}
    cfg.update(train=True,test=False,report_to=None,adapter_path=str(directory/'adapter'),
               iters=job.get('iterations',10 if job['kind']=='short' else 3),save_every=1,
               steps_per_report=1,seed=42+job.get('segment_index',0))
    if job['kind']=='segment' and job.get('checkpoint'):
        cfg['resume_adapter_file']=str(Path(job['checkpoint'])/'adapters.safetensors')
    cfg['model']=str((repo/cfg['model']).resolve());cfg['data']=str((repo/cfg['data']).resolve())
    class Recorder(TrainingCallback):
        def append(self,kind,record):
            if not all(math.isfinite(float(v)) for v in record.values() if isinstance(v,(float,int))):
                raise RuntimeError('Nonfinite training metric')
            if record.get('peak_memory',0)>200:raise RuntimeError('Reported Metal memory exceeds 200 GB')
            with (directory/'metrics.jsonl').open('a') as h:
                h.write(json.dumps({'kind':kind,**record})+'\n');h.flush();os.fsync(h.fileno())
        def on_train_loss_report(self,x):self.append('train',x)
        def on_val_loss_report(self,x):self.append('valid',x)
    np.random.seed(cfg['seed']);model,tokenizer=load(cfg['model'],tokenizer_config={'trust_remote_code':False},trust_remote_code=False)
    assert not model.layers[-1].is_linear and cfg['num_layers']==1
    assert cfg['fine_tune_type']=='lora' and cfg['trust_remote_code'] is False and cfg['report_to'] is None
    args=types.SimpleNamespace(**cfg);a,b,_=load_dataset(args,tokenizer)
    from overnight_controller import atomic_json
    atomic_json(directory/'train-start.json',{'training_api_entered':True,'confirmed_steps':0})
    if cfg.get('frozen_prefix_inference'):
        if cfg['grad_checkpoint']:raise ValueError('Whole-class gradient checkpointing is incompatible with frozen-prefix mode')
        from frozen_prefix_training import frozen_prefix_training
        with frozen_prefix_training(model):train_model(args,model,a,b,Recorder())
    else:
        train_model(args,model,a,b,Recorder())


def reload_check(repo,job,directory):
    import gc
    import mlx.core as mx
    from mlx_lm import load
    from overnight_controller import atomic_json
    model_path=repo.parent/'work/models-derived/ccore-bf16';adapter=job['checkpoint']
    def logits(with_adapter):
        model,tok=load(str(model_path),adapter_path=adapter if with_adapter else None,tokenizer_config={'trust_remote_code':False},trust_remote_code=False)
        model.eval();ids=tok.encode('Write a correct JavaScript GLB export helper.')
        out=model(mx.array([ids]))[:,-1,:].astype(mx.float32);mx.eval(out);result=out.tolist()[0]
        del model,tok,out;gc.collect();mx.clear_cache();return result
    base=logits(False);first=logits(True);second=logits(True)
    finite=all(math.isfinite(x) for values in [base,first,second] for x in values)
    effect=max(abs(a-b) for a,b in zip(base,first));drift=max(abs(a-b) for a,b in zip(first,second))
    result={'finite':finite,'adapter_effect_max_logit_delta':effect,'reload_max_logit_delta':drift,
            'reload_verified':finite and effect>0 and drift<=0.00001,'training_performed_by_reload_check':False}
    atomic_json(directory/'reload.json',result)
    if not result['reload_verified']:raise RuntimeError('Adapter effect/reload check did not pass')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',type=Path,required=True);p.add_argument('--execute-authorized',action='store_true');args=p.parse_args()
    if not args.execute_authorized or os.environ.get('ASTRA_LIVE_WORKER')!='1' or not os.environ.get('GPU_SLOT_HELD'):
        raise SystemExit('Live authorization and GPU slot required; no model loaded')
    job=json.loads(args.job.read_text())
    if job.get('simulated') or not job.get('live_authorized'):raise SystemExit('Refusing simulated/unapproved job')
    repo=Path(__file__).resolve().parents[1];directory=args.job.parent
    if job['kind'] in {'short','length','segment'}:train(repo,job,directory)
    elif job['kind']=='reload':reload_check(repo,job,directory)
    else:raise SystemExit('Unsupported live worker kind')

if __name__=='__main__':main()
