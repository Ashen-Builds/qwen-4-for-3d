"""Process-local optimization for a frozen prefix and final-layer-only LoRA."""
from contextlib import contextmanager


@contextmanager
def frozen_prefix_training(model):
    import mlx.core as mx
    from mlx.utils import tree_flatten
    layers=model.layers
    if len(layers)!=32 or layers[-1].is_linear:raise ValueError('Requires32 layers and final full-attention block')
    final=layers[-1];kind=type(final);original_call=kind.__call__;original_train=model.train
    def assert_scope():
        items=tree_flatten(model.trainable_parameters())
        if not items or not all('.layers.31.' in name and name.rsplit('.',1)[-1] in {'lora_a','lora_b'} for name,_ in items):
            raise ValueError('Refusing to detach a trainable prefix or output head')
    def train(mode=True):
        result=original_train(mode)
        for layer in layers[:-1]:layer.eval()
        if mode:assert_scope()
        return result
    def forward(layer,x,*args,**kwargs):
        if layer is final:x=mx.stop_gradient(x)
        return original_call(layer,x,*args,**kwargs)
    model.train=train;kind.__call__=forward
    try:yield assert_scope
    finally:
        kind.__call__=original_call;model.train=original_train
