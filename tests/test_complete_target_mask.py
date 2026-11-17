"""CPU-only tests: explicit target sets and analytic softmax gradients."""
import ast,contextlib,json,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import complete_target_mask as proposal
import importlib.metadata
try:
    NATIVE_ROOT=Path(importlib.metadata.distribution('mlx-lm').locate_file('mlx_lm'))
except importlib.metadata.PackageNotFoundError:
    NATIVE_ROOT=None

HERE=Path(__file__).resolve().parent

def cross_entropy(logits,targets):
    z=logits-logits.max(axis=-1,keepdims=True)
    return np.log(np.exp(z).sum(axis=-1))-np.take_along_axis(z,targets[...,None],axis=-1)[...,0]

@contextlib.contextmanager
def backend():
    names=['mlx','mlx.core','mlx.nn','mlx_lm','mlx_lm.lora','mlx_lm.tuner','mlx_lm.tuner.trainer']
    modules={n:types.ModuleType(n) for n in names}
    for x in modules.values():x.__path__=[]
    modules['mlx.core'].arange=np.arange;modules['mlx.core'].logical_and=np.logical_and;modules['mlx.core'].float32=np.float32
    modules['mlx.nn'].losses=types.SimpleNamespace(cross_entropy=cross_entropy)
    calls=[]
    def native_train(*args,**kwargs):calls.append(kwargs);return kwargs
    modules['mlx_lm.tuner.trainer'].train=native_train;modules['mlx_lm.lora'].train=native_train
    with patch.dict(sys.modules,modules):yield modules,calls,native_train

class MaskCases(unittest.TestCase):
    def setUp(self):self.b=backend();self.mods,self.calls,self.native=self.b.__enter__()
    def tearDown(self):self.b.__exit__(None,None,None)
    def selected(self,offset,length,width):
        mask=proposal.complete_target_mask(np.array([[offset,length]]),width-1)[0]
        return np.arange(1,width)[mask].tolist()
    def test_padded_toy_keeps_first_and_last_real_assistant_targets(self):self.assertEqual(self.selected(3,5,32),[3,4])
    def test_no_padding(self):self.assertEqual(self.selected(3,5,5),[3,4])
    def test_offset_zero_excludes_unpredictable_first_token_and_all_padding(self):self.assertEqual(self.selected(0,5,32),[1,2,3,4])
    def test_variable_lengths(self):
        mask=proposal.complete_target_mask(np.array([[3,5],[2,8]]),8)
        self.assertEqual(np.flatnonzero(mask[0]).tolist(),[2,3])
        self.assertEqual(np.flatnonzero(mask[1]).tolist(),[1,2,3,4,5,6])
    def test_real_zero_id_is_kept_and_trailing_nonzero_padding_is_excluded(self):
        batch=np.array([[1,2,0,3,4,2,3,1,2]])
        mask=proposal.complete_target_mask(np.array([[2,5]]),8)[0]
        self.assertEqual(batch[:,1:][0,mask].tolist(),[0,3,4])
    def test_actual_repair_counts(self):
        r=json.loads((HERE/'fixtures/repair-mask-case.json').read_text());self.assertEqual(r['real_length'],119);self.assertEqual(r['offset'],72)
        self.assertEqual(self.selected(72,119,129),list(range(72,119)))
        self.assertEqual(len(self.selected(72,119,129)),47)
        self.assertEqual(r['token_ids'][-1],198)
        batch=np.zeros((1,129),dtype=np.int32);batch[0,:119]=r['token_ids']
        self.mods['mlx.nn'].losses.cross_entropy=lambda logits,targets:np.ones(targets.shape,dtype=np.float32)
        loss,nt=proposal.correct_complete_target_loss(lambda unused:None,batch,np.array([[72,119]]))
        self.assertEqual(int(nt),47);self.assertEqual(float(loss),1.0)
    def test_all_masked_rows_have_zero_valid_targets_and_need_preflight_rejection(self):
        self.assertEqual(self.selected(5,5,32),[])
    def test_padding_has_exactly_zero_analytic_gradient(self):
        rng=np.random.default_rng(42);logits=rng.normal(size=(2,8,5))
        batch=np.array([[1,2,0,3,4,2,1,2,3],[1,2,3,4,0,1,2,3,4]])
        lengths=np.array([[2,5],[2,8]]);mask=proposal.complete_target_mask(lengths,8)
        loss,nt=proposal.correct_complete_target_loss(lambda unused:logits,batch,lengths)
        z=logits-logits.max(axis=-1,keepdims=True);prob=np.exp(z)/np.exp(z).sum(axis=-1,keepdims=True)
        onehot=np.eye(5)[batch[:,1:]];gradient=(prob-onehot)*mask[...,None]/nt
        self.assertTrue(np.all(gradient[~mask]==0));self.assertTrue(np.any(gradient[mask]!=0));self.assertEqual(int(nt),9)
        changed=logits.copy();changed[~mask]+=rng.normal(size=changed[~mask].shape)*100
        changed_loss,changed_nt=proposal.correct_complete_target_loss(lambda unused:changed,batch,lengths)
        self.assertEqual(float(changed_loss),float(loss));self.assertEqual(int(changed_nt),int(nt))
        # This is an analytic CPU derivative proof, not MLX backward execution.
    def test_loss_uses_only_explicit_real_positions(self):
        batch=np.array([[0,1,2,3,4,1,2,3]])
        logits=np.arange(35,dtype=np.float64).reshape(1,7,5)/7
        loss,nt=proposal.correct_complete_target_loss(lambda unused:logits,batch,np.array([[3,5]]))
        expected=cross_entropy(logits[:,[2,3]],batch[:,[3,4]]).astype(np.float32).sum()/2
        self.assertEqual(int(nt),2);self.assertAlmostEqual(float(loss),float(expected),places=7)

class HookCases(unittest.TestCase):
    def setUp(self):self.b=backend();self.mods,self.calls,self.native=self.b.__enter__();self.lora=self.mods['mlx_lm.lora']
    def tearDown(self):self.b.__exit__(None,None,None)
    def test_supported_hook_is_passed_and_original_restored(self):
        with proposal.native_complete_target_loss():
            self.lora.train(model='sentinel')
            self.assertIs(self.calls[0]['loss'],proposal.correct_complete_target_loss)
        self.assertIs(self.lora.train,self.native)
    def test_exception_restores_binding(self):
        with self.assertRaisesRegex(ValueError,'sentinel'):
            with proposal.native_complete_target_loss():raise ValueError('sentinel')
        self.assertIs(self.lora.train,self.native)
    def test_prepatched_binding_is_rejected_and_not_overwritten(self):
        foreign=lambda:None;self.lora.train=foreign
        with self.assertRaisesRegex(RuntimeError,'prepatched'):
            with proposal.native_complete_target_loss():pass
        self.assertIs(self.lora.train,foreign)
    def test_nested_context_rejected_outer_still_restored(self):
        with proposal.native_complete_target_loss():
            bound=self.lora.train
            with self.assertRaisesRegex(RuntimeError,'prepatched'):
                with proposal.native_complete_target_loss():pass
            self.assertIs(self.lora.train,bound)
        self.assertIs(self.lora.train,self.native)
    @unittest.skipIf(NATIVE_ROOT is None,'MLX-LM metadata not installed')
    def test_installed_native_train_passes_selected_loss_to_validation(self):
        source=NATIVE_ROOT/'tuner/trainer.py'
        tree=ast.parse(source.read_text());train=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='train')
        calls=[x for x in ast.walk(train) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='evaluate']
        self.assertEqual(len(calls),1)
        self.assertTrue(any(k.arg=='loss' and isinstance(k.value,ast.Name) and k.value.id=='loss' for k in calls[0].keywords))
    @unittest.skipIf(NATIVE_ROOT is None,'MLX-LM metadata not installed')
    def test_native_train_model_uses_global_train_without_overriding_loss(self):
        source=NATIVE_ROOT/'lora.py'
        tree=ast.parse(source.read_text());train_model=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='train_model')
        calls=[x for x in ast.walk(train_model) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='train']
        self.assertEqual(len(calls),1);self.assertNotIn('loss',[k.arg for k in calls[0].keywords])

if __name__=='__main__':
    assert 'mlx' not in sys.modules,'Do not run CPU tests with a real MLX backend imported'
    unittest.main(verbosity=2)
