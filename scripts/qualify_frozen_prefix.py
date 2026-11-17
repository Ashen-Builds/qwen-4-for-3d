"""Measure reference/optimized forward and adapter-gradient agreement under GPU slot."""
import argparse,copy,gc,json,math,os,time
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--adapter',type=Path,required=True);p.add_argument('--reference-mode',choices=['training','deployed-eval'],default='training');args=p.parse_args()
    if not os.environ.get('GPU_SLOT_HELD'):raise SystemExit('GPU slot required')
    import mlx.core as mx,mlx.nn as nn,mlx.optimizers as optim
    import numpy as np
    from mlx.utils import tree_flatten,tree_unflatten
    from mlx_lm import load
    from mlx_lm.tuner.trainer import default_loss
    from frozen_prefix_training import frozen_prefix_training
    repo=Path(__file__).resolve().parents[1];model,tok=load(str(repo.parent/'work/models-derived/ccore-bf16'),adapter_path=str(args.adapter),tokenizer_config={'trust_remote_code':False});mx.set_cache_limit(2*1024**3)
    row=json.loads((repo.parent/'work/sprint-prep/training-ready/repairs/train.jsonl').read_text().splitlines()[0]);ids=tok.apply_chat_template(row['messages'],tokenize=True,return_dict=False);prefix=tok.apply_chat_template(row['messages'][:-1],tokenize=True,return_dict=False,add_generation_prompt=True);batch=mx.array([ids]);lengths=mx.array([[len(prefix),len(ids)-1]])
    model.freeze();model.unfreeze(keys=['lora_a','lora_b'])
    initial_host={name:np.array(w) for name,w in tree_flatten(model.trainable_parameters())};initial={name:mx.array(w) for name,w in initial_host.items()};mx.eval(initial)
    assert initial and all('.layers.31.' in name and name.rsplit('.',1)[-1] in {'lora_a','lora_b'} for name in initial)
    assert sum(w.size for w in initial.values())==479232
    assert initial and any(bool(mx.any(w!=0)) for name,w in initial.items() if name.endswith('lora_b'))
    value_grad=nn.value_and_grad(model,default_loss)
    def measure():
        start=time.monotonic();(loss,ntoks),g=value_grad(model,batch,lengths);logits=model(batch[:,:-1]);mx.eval(loss,g,logits)
        return loss.item(),{n:mx.array(v) for n,v in tree_flatten(g)},mx.array(logits),time.monotonic()-start
    model.train() if args.reference_mode=='training' else model.eval()
    ref_loss,ref_grad,ref_logits,ref_seconds=measure();mx.eval(ref_grad,ref_logits)
    with frozen_prefix_training(model):
        model.train();assert all(not x.training for x in model.layers[:-1]) and model.layers[-1].training
        model.eval();model.train();assert all(not x.training for x in model.layers[:-1]) and model.layers[-1].training
        opt_loss,opt_grad,opt_logits,opt_seconds=measure();mx.eval(opt_grad,opt_logits)
        deltas=[]
        for name in ref_grad:
            a=ref_grad[name].astype(mx.float32);b=opt_grad[name].astype(mx.float32);mx.eval(a,b)
            norm=mx.sqrt(mx.sum(a*a));rel=(mx.sqrt(mx.sum((a-b)**2))/(norm+1e-12)).item();dot=(mx.sum(a*b)/(mx.sqrt(mx.sum(a*a)*mx.sum(b*b))+1e-12)).item()
            deltas.append({'name':name,'relative_l2':rel,'cosine':dot,'reference_norm':norm.item(),'finite':bool(mx.all(mx.isfinite(b)).item()),'absolute_l2':mx.sqrt(mx.sum((a-b)**2)).item()})
        logit_max=mx.max(mx.abs(ref_logits.astype(mx.float32)-opt_logits.astype(mx.float32))).item();loss_diff=abs(ref_loss-opt_loss)
        # Same optimizer state, one small authorized qualification update per branch.
        optA=optim.AdamW(1e-5);optB=optim.AdamW(1e-5)
        model.load_weights([(n,mx.array(w)) for n,w in initial_host.items()],strict=False);optA.update(model,tree_unflatten(list(ref_grad.items())));mx.eval(model.trainable_parameters());updateA={n:mx.array(w) for n,w in tree_flatten(model.trainable_parameters())};mx.eval(updateA)
        model.load_weights([(n,mx.array(w)) for n,w in initial_host.items()],strict=False);optB.update(model,tree_unflatten(list(opt_grad.items())));mx.eval(model.trainable_parameters());updateB=dict(tree_flatten(model.trainable_parameters()));update_delta=max(mx.max(mx.abs(updateA[n]-updateB[n])).item() for n in updateA)
        model.eval();saved_logits=model(batch[:,:-1]);mx.eval(saved_logits)
        args.out.mkdir(parents=True,exist_ok=False);mx.save_safetensors(str(args.out/'adapters.safetensors'),updateB);(args.out/'adapter_config.json').write_bytes((args.adapter/'adapter_config.json').read_bytes())
    del model,value_grad;gc.collect();mx.clear_cache();restored,_=load(str(repo.parent/'work/models-derived/ccore-bf16'),adapter_path=str(args.out),tokenizer_config={'trust_remote_code':False});restored.eval();got=restored(batch[:,:-1]);mx.eval(got);assert got.shape==saved_logits.shape, 'Reload logit shape mismatch';reload_delta=mx.max(mx.abs(got.astype(mx.float32)-saved_logits.astype(mx.float32))).item()
    strict=args.reference_mode=='deployed-eval'
    passed=loss_diff<=(0.00001 if strict else 0.01) and logit_max<=(0.00001 if strict else 0.125) and all(x['finite'] and (x['absolute_l2']<=1e-7 if x['reference_norm']<1e-8 else x['relative_l2']<=(0.00001 if strict else 0.05) and x['cosine']>=0.995) for x in deltas) and update_delta<=(1e-7 if strict else 0.00002) and reload_delta<=0.00001
    result={'passed':passed,'reference_mode':args.reference_mode,'all_sequence_logits_compared':True,'tokens':len(ids),'reference_loss':ref_loss,'optimized_loss':opt_loss,'loss_abs_difference':loss_diff,'max_logit_difference':logit_max,'reference_seconds':ref_seconds,'optimized_seconds':opt_seconds,'gradient_comparison':deltas,'one_update_max_adapter_difference':update_delta,'ordinary_loader_max_logit_difference':reload_delta,'scope':'Trained nonzero adapter, short complete example. All-token logits and each LoRA gradient compared. Deployed-eval oracle uses original unmodified inference kernels with gradients enabled only on the same final-layer LoRA. This does not erase or pass prior training-ops equivalence failure. Two isolated one-step branches; not main training or long-length performance proof.','peak_memory_gb':mx.get_peak_memory()/1e9}
    (args.out/'equivalence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='gradient_comparison'}),flush=True)
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
