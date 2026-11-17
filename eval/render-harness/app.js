import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const renderer = new THREE.WebGLRenderer({canvas:document.querySelector('#canvas'),antialias:true});
renderer.setPixelRatio(1);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const loader=new GLTFLoader(), views=[];
let playing=true, previous=0, sceneTime=0;
const armIds=(document.body.dataset.arms||'qwen,ccore').split(',');
for(const id of armIds){
  const el=document.getElementById(id),scene=new THREE.Scene();
  scene.background=new THREE.Color('#e8e4dc');
  const camera=new THREE.PerspectiveCamera(40,1,.05,1000);
  const controls=new OrbitControls(camera,el);controls.enableDamping=true;
  scene.add(new THREE.HemisphereLight(0xfff7e5,0x6e817e,2.2));
  const sun=new THREE.DirectionalLight(0xffe0ae,3.2);sun.position.set(12,24,15);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xc6e2ff,1.1);fill.position.set(-15,10,-10);scene.add(fill);
  const view={id,el,scene,camera,controls,mixer:null,height:5};views.push(view);reset(view);
  el.querySelectorAll('.bar a').forEach(a=>a.addEventListener('pointerdown',e=>e.stopPropagation()));
  fetch(`./${id}/result.json`).then(r=>r.json()).then(r=>{view.variant=r.display_variant||'Unlabeled export'}).catch(()=>{view.variant='Unlabeled export'}).then(()=>fetch(`./${id}/asset.glb`,{method:'HEAD'})).then(r=>{
    if(!r.ok)throw new Error('Export unavailable');
    loader.load(`./${id}/asset.glb`,gltf=>{
      const root=gltf.scene;
      root.traverse(o=>{if(o.isLight)o.visible=false});
      const box=new THREE.Box3().setFromObject(root),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
      const scale=20/Math.max(size.x,size.y,size.z,.001);
      const wrapper=new THREE.Group();wrapper.add(root);wrapper.scale.setScalar(scale);
      wrapper.position.set(-center.x*scale,-box.min.y*scale,-center.z*scale);scene.add(wrapper);
      view.mixer=new THREE.AnimationMixer(root);for(const clip of gltf.animations)view.mixer.clipAction(clip).play();view.mixer.setTime(sceneTime);
      view.height=size.y*scale; reset(view);
      el.querySelector('.status').hidden=true;el.querySelector('a').hidden=false;
      let meshes=0,triangles=0;root.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?o.geometry.index.count:o.geometry.attributes.position.count)/3*(o.count||1)}});
      el.querySelector('.stats').textContent=`${meshes.toLocaleString()} meshes · ${Math.round(triangles).toLocaleString()} triangles · ${gltf.animations.length} clips · ${view.variant||'Unlabeled export'}`;
      view.report={meshes,triangles,clips:gltf.animations.length,originalBounds:size.toArray(),viewerScale:scale};
      window.comparisonReports=Object.fromEntries(views.filter(v=>v.report).map(v=>[v.id,v.report]));
    },undefined,e=>{el.querySelector('.status').textContent='GLB load failed';console.error(id,e)});
  }).catch(()=>{});
}
function reset(v){v.camera.position.set(21,17+v.height*.2,24);v.controls.target.set(0,v.height*.35,0);v.controls.update()}
document.querySelector('#reset').onclick=()=>views.forEach(reset);
for(const button of document.querySelectorAll('[data-time]'))button.onclick=()=>{sceneTime=Number(button.dataset.time);playing=false;document.querySelector('#play').textContent='Play';for(const view of views)view.mixer?.setTime(sceneTime);window.comparisonTimeSeconds=sceneTime;};
document.querySelector('#play').onclick=e=>{playing=!playing;e.target.textContent=playing?'Pause':'Play'};
function frame(now){requestAnimationFrame(frame);if(now-previous<1000/60-.5)return;const dt=Math.min((now-previous)/1000,.1);previous=now;if(playing)sceneTime+=dt;window.comparisonTimeSeconds=sceneTime;
  const width=innerWidth,height=innerHeight-72;renderer.setSize(width,height,false);renderer.setScissorTest(true);
  for(const v of views){const r=v.el.getBoundingClientRect();v.camera.aspect=r.width/r.height;v.camera.updateProjectionMatrix();v.controls.update();if(playing)v.mixer?.update(dt);
    renderer.setViewport(r.left,0,r.width,height);renderer.setScissor(r.left,0,r.width,height);renderer.render(v.scene,v.camera)}
}
requestAnimationFrame(frame);
