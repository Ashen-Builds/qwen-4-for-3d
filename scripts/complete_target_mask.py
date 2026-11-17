"""Private proposal: correct the end bound without changing installed files.

Native iterate_batches returns [prompt_offset, real_token_count]. Shifted target
positions are1..width-1, so real targets satisfy offset<=position<token_count.
No MLX or model is imported until the functions/context are actually invoked.
"""
from contextlib import contextmanager
from functools import partial


def complete_target_mask(lengths,target_width):
    import mlx.core as mx
    steps=mx.arange(1,target_width+1)
    return mx.logical_and(steps>=lengths[:,0:1],steps<lengths[:,1:])


def correct_complete_target_loss(model,batch,lengths):
    import mlx.core as mx
    import mlx.nn as nn
    inputs=batch[:,:-1]
    targets=batch[:,1:]
    logits=model(inputs)
    mask=complete_target_mask(lengths,targets.shape[1])
    ce=nn.losses.cross_entropy(logits,targets)*mask
    ntoks=mask.sum()
    ce=ce.astype(mx.float32).sum()/ntoks
    return ce,ntoks


@contextmanager
def native_complete_target_loss():
    """Preserve native train_model setup; pass the supported trainer loss hook.

    Enter only in an owned idle process before train_model. Reject a foreign or
    nested binding. Native trainer propagates this same loss to validation.
    Restore the exact original binding on normal or exceptional exit.
    """
    import mlx_lm.lora as lora
    from mlx_lm.tuner.trainer import train as native_train
    if lora.train is not native_train:
        raise RuntimeError('Refusing an unexpected prepatched mlx_lm.lora.train binding')
    original=lora.train
    lora.train=partial(native_train,loss=correct_complete_target_loss)
    try:
        yield
    finally:
        lora.train=original
