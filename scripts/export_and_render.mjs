#!/usr/bin/env node
// Run one generated asset page in headless Chrome (software GL, no GPU slot),
// click its own Export GLB button, validate the download and render two common
// views. The model's program is never edited beyond the dependency-URL staging
// done by stage_generated_page.py.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import validator from 'gltf-validator';

const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = {};
for (let i = 2; i < process.argv.length; i += 2) args[process.argv[i].replace(/^--/, '')] = process.argv[i + 1];
if (!args.run || !args.out) throw Error('Usage: export_and_render.mjs --run RUN_DIR --out OUT_DIR');
const RUN = path.resolve(args.run), OUT = path.resolve(args.out);
fs.mkdirSync(OUT, { recursive: true });
const result = { schema: 1, status: 'unknown', run: RUN, page_errors: [], console_errors: [], external_requests: [] };
const finish = status => {
  result.status = status;
  fs.writeFileSync(path.join(OUT, 'result.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({ status, glb_bytes: result.glb?.bytes, animations: result.glb?.animations?.length, page_errors: result.page_errors.length }));
};

if (!fs.existsSync(path.join(RUN, 'generated.html'))) { finish('no_html'); process.exit(0); }
const staged = spawnSync('python3', [path.join(REPO, 'scripts/stage_generated_page.py'), '--run', RUN, '--destination', OUT], { encoding: 'utf8' });
if (staged.status !== 0) { result.stage_error = staged.stderr; finish('stage_failed'); process.exit(0); }

const VIEWER = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#262a31}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"/vendor/three/build/three.module.js","three/addons/":"/vendor/three/examples/jsm/"}}</script></head><body>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const S = 768;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(S, S);
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x262a31);
scene.add(new THREE.HemisphereLight(0xffffff, 0x50545c, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 2.2); scene.add(key);
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 1000);
try {
  const gltf = await new GLTFLoader().loadAsync('/asset.glb');
  scene.add(gltf.scene);
  if (gltf.animations.length) { const m = new THREE.AnimationMixer(gltf.scene); gltf.animations.forEach(c => m.clipAction(c).play()); m.setTime(0); }
  gltf.scene.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(gltf.scene), c = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const r = Math.max(size.length() / 2, 1e-4), d = r / Math.sin(THREE.MathUtils.degToRad(35 / 2)) * 1.08;
  camera.near = d / 100; camera.far = d * 10; camera.updateProjectionMatrix();
  window.__size = size.toArray();
  window.__view = az => {
    const a = THREE.MathUtils.degToRad(az), e = THREE.MathUtils.degToRad(18);
    camera.position.set(c.x + d * Math.sin(a) * Math.cos(e), c.y + d * Math.sin(e), c.z + d * Math.cos(a) * Math.cos(e));
    camera.lookAt(c); key.position.copy(camera.position).add(new THREE.Vector3(r, 2 * r, 0));
    renderer.render(scene, camera);
  };
  window.__view(35); window.__ready = true;
} catch (e) { window.__error = String(e); }
</script></body></html>`;

const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.wasm': 'application/wasm' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/__viewer.html') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end(VIEWER); }
  const root = url.startsWith('/vendor/three/') ? path.join(REPO, 'node_modules/three') : OUT;
  const rel = url.startsWith('/vendor/three/') ? url.slice('/vendor/three/'.length) : url.slice(1);
  const file = path.resolve(root, rel);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;
const profile = fs.mkdtempSync(path.join(OUT, '.chrome-'));
const context = await chromium.launchPersistentContext(profile, {
  channel: 'chrome', headless: true, acceptDownloads: true, viewport: { width: 1024, height: 768 },
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--mute-audio', '--no-first-run'],
});
let status = 'unknown';
try {
  const page = await context.newPage();
  page.on('pageerror', e => result.page_errors.push(String(e.message || e).slice(0, 500)));
  page.on('console', m => { if (m.type() === 'error') result.console_errors.push(m.text().slice(0, 500)); });
  page.on('request', r => { if (!r.url().startsWith(base) && !r.url().startsWith('blob:') && !r.url().startsWith('data:')) result.external_requests.push(r.url().slice(0, 200)); });
  await page.goto(base + '/generated.html', { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(OUT, 'page.png') });
  const buttons = page.locator('button, input[type=button], a').filter({ hasText: /export|download|glb/i });
  result.export_buttons = await buttons.count();
  let download = null;
  if (result.export_buttons) {
    try {
      [download] = await Promise.all([page.waitForEvent('download', { timeout: 45000 }), buttons.first().click({ timeout: 10000 })]);
    } catch (e) { result.export_error = String(e.message || e).slice(0, 300); }
  }
  if (!download) status = result.page_errors.length ? 'page_error' : 'no_export';
  else {
    const glb = path.join(OUT, 'asset.glb');
    await download.saveAs(glb);
    const bytes = fs.readFileSync(glb);
    result.glb = { suggested_name: download.suggestedFilename(), bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
    if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF') status = 'invalid_glb';
    else {
      const report = await validator.validateBytes(new Uint8Array(bytes), { uri: 'asset.glb', maxIssues: 500 });
      const doc = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString('utf8'));
      Object.assign(result.glb, { validator_errors: report.issues.numErrors, validator_warnings: report.issues.numWarnings,
        meshes: doc.meshes?.length || 0, nodes: doc.nodes?.length || 0, materials: doc.materials?.length || 0,
        skins: doc.skins?.length || 0, textures: doc.textures?.length || 0,
        triangles: report.info?.totalTriangleCount ?? null,
        animations: (doc.animations || []).map(a => ({ name: a.name || '', channels: a.channels?.length || 0 })) });
      status = report.issues.numErrors ? 'invalid_glb' : 'ok';
      const viewer = await context.newPage();
      await viewer.setViewportSize({ width: 768, height: 768 });
      await viewer.goto(base + '/__viewer.html', { waitUntil: 'load' });
      await viewer.waitForFunction('window.__ready || window.__error', null, { timeout: 60000 });
      const err = await viewer.evaluate('window.__error || null');
      if (err) { result.viewer_error = err; status = 'invalid_glb'; }
      else {
        result.glb.size_xyz = await viewer.evaluate('window.__size');
        for (const [name, az] of [['view-front', 35], ['view-back', 215]]) {
          await viewer.evaluate(a => window.__view(a), az);
          await viewer.locator('canvas').screenshot({ path: path.join(OUT, name + '.png') });
        }
      }
    }
  }
} catch (e) { result.harness_error = String(e.stack || e).slice(0, 800); status = 'harness_error'; }
finally { await context.close(); server.close(); fs.rmSync(profile, { recursive: true, force: true }); }
finish(status);
