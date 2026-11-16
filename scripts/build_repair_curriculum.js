// Trusted API repair examples, checked against a real licensed GLB; no training.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import validator from 'gltf-validator';
const [candidate,out]=process.argv.slice(2);if(!candidate||!out)throw new Error('Usage: node scripts/build_repair_curriculum.js REPLAY_CANDIDATE OUTPUT');
if(fs.existsSync(out))throw new Error('Output exists');fs.mkdirSync(out,{recursive:true});
globalThis.FileReader=class {readAsArrayBuffer(b){b.arrayBuffer().then(v=>{this.result=v;this.onload?.();this.onloadend?.()})}readAsDataURL(b){b.arrayBuffer().then(v=>{this.result=`data:${b.type};base64,${Buffer.from(v).toString('base64')}`;this.onload?.();this.onloadend?.()})}};
const prov=JSON.parse(fs.readFileSync(path.join(candidate,'PROVENANCE.json')));
let selected,source;
for(const item of prov.selected.filter(x=>x.provided_glb_animations>0)){
 const b=fs.readFileSync(path.join(candidate,'provided-glbs',item.id+'.glb'));const doc=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());if(doc.images?.length)continue;selected=item;source=b;break;
}
if(!source)throw new Error('Need self-contained textured-image-free animated source');
const load=()=>new GLTFLoader().parseAsync(source.buffer.slice(source.byteOffset,source.byteOffset+source.byteLength),'');
const families=[
 ['export_async','Export the complete loaded scene and all its existing animation clips as a binary GLB. Use the Promise API.',`async function exportAsset(gltf) { return await new GLTFExporter().parseAsync(gltf.scene, { binary: true, animations: gltf.animations, onlyVisible: false }); }`,'export'],
 ['export_callback','Wrap the GLTFExporter callback API in a Promise. Put callbacks and options in their correct argument positions and preserve existing animations.',`function exportAsset(gltf) { return new Promise((resolve, reject) => { new GLTFExporter().parse(gltf.scene, resolve, reject, { binary: true, animations: gltf.animations, onlyVisible: false }); }); }`,'export'],
 ['quaternion_values','Build a quaternion track from supplied Quaternion samples. Bind to the supplied object UUID and flatten numeric values; keep samples unchanged.',`function makeTrack(target, times, samples) { const values = samples.flatMap(q => q.toArray()); return new THREE.QuaternionKeyframeTrack(target.uuid + '.quaternion', times, values); }`,'quaternion'],
 ['vector_values','Build a position track from supplied Vector3 samples. Keep the existing values and bind to the object UUID.',`function makeTrack(target, times, samples) { return new THREE.VectorKeyframeTrack(target.uuid + '.position', times, samples.flatMap(v => v.toArray())); }`,'vector'],
 ['retain_hierarchy','Return the full export root from a loaded GLTF. Do not pick only its first child or discard siblings.',`function exportRoot(gltf) { return gltf.scene; }`,'root'],
 ['finite_tracks','Return a copy of an existing animation clip with malformed value-size or nonfinite tracks removed. Retain good curves unchanged.',`function cleanClip(clip) { const tracks = clip.tracks.filter(t => t.times.length > 0 && t.values.length > 0 && t.values.length % t.times.length === 0 && Array.from(t.times).every(Number.isFinite) && Array.from(t.values).every(Number.isFinite)); return new THREE.AnimationClip(clip.name, clip.duration, tracks.map(t => t.clone())); }`,'clean'],
 ['independent_clips','Copy the loaded animation clips for independent use without sharing mutable track arrays.',`function copyClips(gltf) { return gltf.animations.map(clip => clip.clone()); }`,'clone'],
 ['mixer_actions','Create a mixer for the complete scene and play each existing clip using the public mixer API. Do not instantiate AnimationAction directly.',`function playClips(gltf) { const mixer = new THREE.AnimationMixer(gltf.scene); for (const clip of gltf.animations) mixer.clipAction(clip).play(); return mixer; }`,'mixer'],
 ['clip_duration','Copy a clip, infer its duration from its existing tracks, and preserve its interpolation and values.',`function resetDuration(clip) { const copy = clip.clone(); copy.resetDuration(); return copy; }`,'duration'],
 ['typed_binary','Return an exact ArrayBuffer view of a Uint8Array without including unrelated backing-buffer bytes.',`function exactBuffer(bytes) { return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength); }`,'buffer'],
];
const train=[],valid=[],checks=[];
const suffixes=['Keep existing geometry and motion intact.','Use Three.js r160 public APIs.','Return only a complete JavaScript function.','Avoid changing the supplied scene content.','The caller supplies THREE and GLTFExporter.','Keep the helper reusable for another loaded GLTF.','Do not introduce new meshes or animation curves.','Make the data safe for subsequent GLB export.'];
for(let index=0;index<families.length;index++){
 const [family,task,code,kind]=families[index];const gltf=await load();if(!gltf.animations.length)throw new Error('Missing source animation');
 const fn=new Function('THREE','GLTFExporter',`return (${code})`)(THREE,GLTFExporter);let result;
 if(kind==='export'){
  result=await fn(gltf);if(!(result instanceof ArrayBuffer))throw new Error(family+' not binary');const doc=JSON.parse(Buffer.from(result).subarray(20,20+new DataView(result).getUint32(12,true)).toString());
  if(!doc.animations?.length)throw new Error('Animation lost');const v=await validator.validateBytes(new Uint8Array(result),{maxIssues:50});if(v.issues.numErrors)throw new Error('Invalid actual GLB');
 }else if(kind==='quaternion'){
  const original=gltf.animations.flatMap(x=>x.tracks).find(t=>t.name.endsWith('.quaternion'));if(!original)throw new Error('No quaternion track');const samples=Array.from(original.times,(_,i)=>new THREE.Quaternion().fromArray(original.values,i*4));result=fn(gltf.scene,Array.from(original.times),samples);
  if(result.values.length!==result.times.length*4||!Array.from(result.values).every(Number.isFinite)||result.name!==gltf.scene.uuid+'.quaternion')throw new Error('Malformed quaternion track');
 }else if(kind==='vector'){
  const times=[0,1],samples=[gltf.scene.position.clone(),gltf.scene.position.clone()];result=fn(gltf.scene,times,samples);if(result.values.length!==6||!Array.from(result.values).every(Number.isFinite))throw new Error('Malformed vector track');
 }else if(kind==='root'){if(fn(gltf)!==gltf.scene)throw new Error('Lost hierarchy');}
 else if(kind==='clean'){const c=gltf.animations[0].clone(),n=c.tracks.length;const bad=c.tracks[0].clone();bad.values[0]=NaN;c.tracks.push(bad);result=fn(c);if(result.tracks.length!==n||result.tracks.some(t=>Array.from(t.values).some(v=>!Number.isFinite(v))))throw new Error('Invalid curve retained');}
 else if(kind==='clone'){result=fn(gltf);if(result[0]===gltf.animations[0]||result[0].tracks[0].values===gltf.animations[0].tracks[0].values)throw new Error('Mutable arrays shared');}
 else if(kind==='mixer'){result=fn(gltf);const action=result.existingAction(gltf.animations[0]);result.update(.25);if(!action||!action.isRunning()||action.time<=0)throw new Error('Action not advancing');}
 else if(kind==='duration'){result=fn(gltf.animations[0]);if(!(result.duration>0)||result===gltf.animations[0])throw new Error('Duration/copy failed');}
 else if(kind==='buffer'){const backing=new Uint8Array([99,1,2,3,98]);result=fn(backing.subarray(1,4));if(Array.from(new Uint8Array(result)).join(',')!=='1,2,3')throw new Error('Backing buffer leaked');}
 const split=index<8?'train':'valid';
 for(const suffix of suffixes){const row={messages:[{role:'system',content:'You are a careful Three.js coding assistant. Return correct complete helper code for the requested operation. Preserve supplied assets and existing animation.'},{role:'user',content:task+' '+suffix},{role:'assistant',reasoning_content:'Use public interfaces and preserve the supplied geometry and animation.',content:'```javascript\n'+code+'\n```'}]};(split==='train'?train:valid).push(row);}
 checks.push({family,split,passed:true,code_sha256:crypto.createHash('sha256').update(code).digest('hex')});
}
for(const [name,rows]of [['train',train],['valid',valid]])fs.writeFileSync(path.join(out,name+'.jsonl'),rows.map(x=>JSON.stringify(x)).join('\n')+'\n');
const report={kind:'New targeted API curriculum authored for observed export/track/action failure classes',rows:{train:train.length,valid:valid.length},program_families:{train:8,valid:2},wording_variants_per_family:8,qualification:'Wording variants are not independent programs. CPU checks use a licensed publisher GLB; two exporter helpers produce actual validator-passing animated GLBs. This does not prove full-scene visual quality or a training gain.',source_asset:{repo:'ccore/ThreeJS-3D-GLB-Assets',revision:'276821245d5714b95571465569ed5b844ac6adc7',id:selected.id,license:'MIT declaration; retained source notice'},checks};
fs.writeFileSync(path.join(out,'CURRICULUM_REPORT.json'),JSON.stringify(report,null,2)+'\n');fs.copyFileSync(path.join(candidate,'LICENSE.source'),path.join(out,'LICENSE.source'));console.log(JSON.stringify(report));
