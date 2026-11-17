import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Viewer-only normalization; source GLB bytes and animation tracks are unchanged.
const cases = {
  babylon: { title:'No Babylon improvement. Both files required mechanical repairs. Astra has 16 actors, but static legs, path snaps and a collapsed canal.', paths:['../diagnostic-thinking48/control/asset.glb','../diagnostic-thinking48/ours/asset.glb'], names:['CCORE BF16 · assisted','Astra 48 · assisted'] },
  waterwheel: { title:'Narrow motion win: Astra rotates around its axle; CCORE swivels around the wrong axis. One task, one seed; both raw exports.', paths:['../final-tests/waterwheel-control/asset.glb','../final-tests/waterwheel-astra/asset.glb'], names:['CCORE · raw','Astra 48 · raw'] },
  orrery: { title:'Export regression: CCORE produced a static file; Astra failed during initialization. Neither completed the requested animation.', paths:['../final-tests/orrery-control/asset.glb',null], names:['CCORE · raw, static','Astra 48 · raw failure'] },
  historical: { title:'The original CCORE visual reference remains preserved. Both displayed Babylon files are repair-assisted diagnostics.', paths:['../ccore/asset.glb','../diagnostic-thinking48/ours/asset.glb'], names:['Original CCORE · assisted','Astra 48 · assisted'] }
};
const renderer = new THREE.WebGLRenderer({canvas:document.querySelector('#canvas'),antialias:true});
renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1;
const loader=new GLTFLoader(),views=[];
let playing=false,sceneTime=0,last=0,frameId=null,revision=0;
const play=document.querySelector('#play');
function requestFrame(){if(frameId===null)frameId=requestAnimationFrame(frame);}
function reset(v){v.camera.position.set(25,19,29);v.controls.target.set(0,0,0);v.controls.update();}
for(const id of document.body.dataset.arms.split(',')){
  const el=document.getElementById(id),scene=new THREE.Scene();scene.background=new THREE.Color('#e8e4dc');
  const camera=new THREE.PerspectiveCamera(40,1,.05,1000),controls=new OrbitControls(camera,el);
  controls.enableDamping=false;controls.addEventListener('change',requestFrame);
  scene.add(new THREE.HemisphereLight(0xfff7e5,0x6e817e,2.2));
  const sun=new THREE.DirectionalLight(0xffe0ae,3.2);sun.position.set(12,24,15);scene.add(sun);
  const fill=new THREE.DirectionalLight(0xc6e2ff,1.1);fill.position.set(-15,10,-10);scene.add(fill);
  const v={el,scene,camera,controls,wrapper:null,mixer:null};views.push(v);reset(v);
}
function dispose(v){if(!v.wrapper)return;v.mixer?.stopAllAction();const geometries=new Set(),materials=new Set(),textures=new Set();v.wrapper.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of (Array.isArray(o.material)?o.material:[o.material]))if(m){materials.add(m);for(const x of Object.values(m))if(x?.isTexture)textures.add(x);}});for(const x of [...geometries,...materials,...textures])x.dispose();v.scene.remove(v.wrapper);v.wrapper=null;v.mixer=null;}
async function loadCase(key){
  const current=++revision,c=cases[key];playing=false;sceneTime=0;play.textContent='Play';document.querySelector('#verdict').textContent=c.title;
  window.comparisonReports={};
  await Promise.all(views.map(async(v,i)=>{
    dispose(v);reset(v);const status=v.el.querySelector('.status'),link=v.el.querySelector('.bar a');
    v.el.querySelector('h2').textContent=c.names[i];v.el.querySelector('.stats').textContent='';status.hidden=false;link.hidden=true;
    if(!c.paths[i]){status.textContent='No GLB — ReferenceError: duration is not defined';requestFrame();return;}
    status.textContent='Loading actual GLB…';
    try{
      const gltf=await loader.loadAsync(c.paths[i]);if(current!==revision)return;
      const root=gltf.scene;root.traverse(o=>{if(o.isLight)o.visible=false;});
      const mixer=new THREE.AnimationMixer(root);for(const clip of gltf.animations)mixer.clipAction(clip).play();mixer.setTime(0);root.updateMatrixWorld(true);
      const box=new THREE.Box3().setFromObject(root),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),scale=20/Math.max(size.x,size.y,size.z,.001);
      const wrapper=new THREE.Group();wrapper.add(root);wrapper.scale.setScalar(scale);wrapper.position.copy(center).multiplyScalar(-scale);v.scene.add(wrapper);v.wrapper=wrapper;v.mixer=mixer;
      let meshes=0;root.traverse(o=>{if(o.isMesh)meshes++;});
      v.el.querySelector('.stats').textContent=`${meshes} meshes · ${gltf.animations.length} clips · ${c.names[i].includes('assisted')?'Repair-assisted; raw source failed':'Unrepaired model output'}`;
      status.hidden=true;link.href=c.paths[i];link.hidden=false;
      window.comparisonReports[i]={meshes,clips:gltf.animations.length,viewerScale:scale,originalBounds:size.toArray()};requestFrame();
    }catch(error){status.textContent='GLB load failed';console.error(error);requestFrame();}
  }));requestFrame();
}
function frame(now){
  frameId=null;
  if(playing && now-last<1000/30-.5){requestFrame();return;}
  const dt=last?Math.min((now-last)/1000,.1):0;last=now;if(playing)sceneTime+=dt;
  window.comparisonTimeSeconds=sceneTime;
  const top=document.querySelector('#canvas').getBoundingClientRect().top;
  renderer.setSize(innerWidth,innerHeight-top,false);renderer.setScissorTest(true);
  for(const v of views){const r=v.el.getBoundingClientRect();v.camera.aspect=r.width/r.height;v.camera.updateProjectionMatrix();v.mixer?.setTime(sceneTime);renderer.setViewport(r.left,innerHeight-r.bottom,r.width,r.height);renderer.setScissor(r.left,innerHeight-r.bottom,r.width,r.height);renderer.render(v.scene,v.camera);}
  if(playing)requestFrame();
}
document.querySelector('#case').onchange=e=>loadCase(e.target.value);
document.querySelector('#reset').onclick=()=>{views.forEach(reset);requestFrame();};
play.onclick=()=>{playing=!playing;last=0;play.textContent=playing?'Pause':'Play';requestFrame();};
for(const b of document.querySelectorAll('[data-time]'))b.onclick=()=>{sceneTime=Number(b.dataset.time);playing=false;play.textContent='Play';requestFrame();};
window.addEventListener('resize',requestFrame);
document.addEventListener('visibilitychange',()=>{if(document.hidden){playing=false;play.textContent='Play';}else requestFrame();});
loadCase('babylon');
