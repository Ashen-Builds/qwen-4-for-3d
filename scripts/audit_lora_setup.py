"""Load and inspect an untrained adapter setup; no forward, gradients or optimizer."""
import argparse
import json
import os
from pathlib import Path
from collections import Counter
import math


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if not os.environ.get('GPU_SLOT_HELD'):raise SystemExit('Run through shared gpu_slot')
    if (Path.home()/'.cache/gpu-slot/STREAMING').exists():raise SystemExit('Streaming guard active')
    import mlx.core as mx
    from mlx.utils import tree_flatten
    from mlx_lm import load
    from mlx_lm.tuner.utils import linear_to_lora_layers
    model,_=load(args.model,tokenizer_config={'trust_remote_code':False});model.eval();model.freeze()
    assert not model.layers[-1].is_linear,'Fast pilot requires final full-attention layer'
    base=tree_flatten(model.parameters());dtypes=Counter(str(x.dtype) for _,x in base)
    linear_to_lora_layers(model,1,{'rank':8,'scale':20.0,'dropout':0.0},use_dora=False)
    items=tree_flatten(model.trainable_parameters());mx.eval([x for _,x in items])
    assert items and all('lora_a' in n or 'lora_b' in n for n,_ in items)
    assert all(bool(mx.all(x==0).item()) for n,x in items if n.endswith('lora_b'))
    receipt={'scope':'Untrained module attachment and dtype/shape audit; no model forward, optimizer, gradients or weight updates','trained_steps':0,'model_file_directory':Path(args.model).name,'layers':len(model.layers),'adapted_last_layers':1,'final_layer_full_attention':True,'base_tensor_dtypes':dict(dtypes),'base_parameters':sum(math.prod(x.shape) for _,x in base),'trainable_parameters':sum(math.prod(x.shape) for _,x in items),'trainable_tensors':[{'name':n,'shape':list(x.shape),'dtype':str(x.dtype)} for n,x in items],'initial_lora_b_zero':True,'gradient_save_reload_throughput_qualified':False,'precision_note':'Original checkpoint preserved; task-derived text weights converted to BF16 through official loader/converter.'}
    args.out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='trainable_tensors'}))

if __name__=='__main__':main()
