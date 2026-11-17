#!/usr/bin/env node
// CPU-only comparison of an actual exported GLB with its supplied reference.
// No renderer, browser, model, export fabrication, dependency installation or mutation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const USAGE = `Usage: node verify_full_program_export.mjs --repo PATH [--workspace PATH] --reference FILE --actual FILE --out JSON

CPU-only comparison using the installed three and gltf-validator dependencies in
--repo. Relative input/output paths resolve against --workspace (default: cwd).
--repo and --workspace themselves resolve against cwd. No dependencies are
loaded and no files are written for --help. No browser, renderer or model runs.
`;
if (process.argv.slice(2).includes('--help')) {
  process.stdout.write(USAGE);
  process.exit(0);
}
const options = {};
const accepted = new Set(['--repo', '--workspace', '--reference', '--actual', '--out']);
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i], value = process.argv[i + 1];
  if (!accepted.has(key) || !value || value.startsWith('--') || options[key.slice(2)] !== undefined) throw Error(USAGE);
  options[key.slice(2)] = value;
}
if (!options.repo || !options.reference || !options.actual || !options.out) throw Error('--repo, --reference, --actual and --out are required.\n' + USAGE);
const REPO = path.resolve(options.repo);
const workspace = path.resolve(options.workspace || process.cwd());
const args = Object.fromEntries(['reference', 'actual', 'out'].map(key => [key, path.resolve(workspace, options[key])]));
if ([args.reference, args.actual].includes(args.out)) throw Error('Output report must not replace an input');

// Resolve dependencies only after help and argument checks. Dependencies remain
// owned and version-pinned by the caller's repository; nothing is installed here.
const require = createRequire(path.join(REPO, 'package.json'));
const validator = require('gltf-validator');
const THREE = await import(pathToFileURL(path.join(REPO, 'node_modules/three/build/three.module.js')));
const { GLTFLoader } = await import(pathToFileURL(path.join(REPO, 'node_modules/three/examples/jsm/loaders/GLTFLoader.js')));

const report = { schema: 2, verifier_version: 'captured-pose-properties-v2', status: 'FAIL', scope: 'CPU binary/content/animation comparison; not browser execution or visual acceptance',
  tolerance: { absolute: 1e-5, relative: 1e-6 }, inputs: {}, failures: [], warnings: [], checks: {},
  limitations: [
    'Only self-contained, image-free, skin-free GLBs are qualified by this verifier; other inputs fail closed.',
    'Geometry accessors are decoded independently of buffer packing, but vertex reordering or primitive repartitioning may conservatively fail equivalent geometry.',
    'Extra non-rendering identity wrappers absent from reference may be ignored only above a single root; named reference hierarchy is retained.',
    'Primitive material definitions are compared after dropping names/extras; material-definition count changes are reported separately.',
    'Animation comparison includes curves, binding existence and CPU world-matrix samples; it does not judge contacts, aesthetics or browser controls.',
    'Only changed local TRS properties explicitly targeted by identical matching animation channels may differ as captured poses, after all curves/bindings and canonical world samples match. Static properties remain mandatory; shear/singular decompositions fail closed.',
    'A passing comparison to a publisher binary does not establish that the source program rendered or that an actual user download occurred.'
  ] };
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const stable = value => {
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + stable(value[k])).join(',') + '}';
  return JSON.stringify(value);
};
const fail = (kind, detail) => report.failures.push({ kind, ...detail });
const near = (a, b) => Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= 1e-5 + 1e-6 * Math.max(Math.abs(a), Math.abs(b));
function equal(a, b) {
  if (typeof a === 'number' && typeof b === 'number') return near(a, b);
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((x, i) => equal(x, b[i]));
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const ak = Object.keys(a).sort(), bk = Object.keys(b).sort();
    return stable(ak) === stable(bk) && ak.every(k => equal(a[k], b[k]));
  }
  return a === b;
}

function parse(file) {
  const bytes = fs.readFileSync(file);
  if (bytes.length < 20 || bytes.readUInt32LE(0) !== 0x46546c67 || bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) throw Error('Invalid GLB magic/version/declared length: ' + file);
  let doc, bin;
  for (let offset = 12; offset < bytes.length;) {
    const length = bytes.readUInt32LE(offset), type = bytes.readUInt32LE(offset + 4);
    if (offset + 8 + length > bytes.length) throw Error('GLB chunk outside file');
    const chunk = bytes.subarray(offset + 8, offset + 8 + length);
    if (type === 0x4e4f534a) { if (doc) throw Error('Duplicate JSON chunk'); doc = JSON.parse(chunk.toString('utf8').trim()); }
    if (type === 0x004e4942) { if (bin) throw Error('Duplicate BIN chunk'); bin = chunk; }
    offset += 8 + length;
  }
  if (!doc || !bin) throw Error('Missing JSON or binary chunk');
  if ((doc.images?.length || 0) || (doc.skins?.length || 0)) throw Error('Image/skin input is outside this bounded verifier');
  if ((doc.buffers || []).some(b => b.uri) || (doc.buffers?.length || 0) !== 1) throw Error('External/multiple buffers are unsupported');
  return { file, bytes, doc, bin, cache: new Map() };
}
const typeSize = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT2: 4, MAT3: 9, MAT4: 16 };
const component = {
  5120: [1, 'readInt8'], 5121: [1, 'readUInt8'], 5122: [2, 'readInt16LE'],
  5123: [2, 'readUInt16LE'], 5125: [4, 'readUInt32LE'], 5126: [4, 'readFloatLE']
};
function accessor(g, index) {
  if (g.cache.has(index)) return g.cache.get(index);
  const a = g.doc.accessors[index], n = typeSize[a.type], [bytesPer, method] = component[a.componentType] || [];
  if (!n || !bytesPer || a.type.startsWith('MAT')) throw Error('Unsupported geometry/animation accessor type');
  let values = new Array(a.count * n).fill(0);
  const read = (viewIndex, byteOffset, count, size, ctype) => {
    const view = g.doc.bufferViews[viewIndex], [width, reader] = component[ctype], stride = view.byteStride || width * size;
    if (view.buffer !== 0) throw Error('Non-BIN buffer view');
    const start = (view.byteOffset || 0) + (byteOffset || 0), result = [];
    for (let i = 0; i < count; i++) for (let j = 0; j < size; j++) result.push(g.bin[reader](start + i * stride + j * width));
    return result;
  };
  if (a.bufferView !== undefined) values = read(a.bufferView, a.byteOffset, a.count, n, a.componentType);
  if (a.sparse) {
    const indices = read(a.sparse.indices.bufferView, a.sparse.indices.byteOffset, a.sparse.count, 1, a.sparse.indices.componentType);
    const updates = read(a.sparse.values.bufferView, a.sparse.values.byteOffset, a.sparse.count, n, a.componentType);
    indices.forEach((v, i) => { for (let j = 0; j < n; j++) values[v * n + j] = updates[i * n + j]; });
  }
  if (a.normalized && a.componentType !== 5126) values = values.map(v => a.componentType === 5120 ? Math.max(-1, v / 127) : a.componentType === 5122 ? Math.max(-1, v / 32767) : v / ({ 5121: 255, 5123: 65535, 5125: 4294967295 }[a.componentType]));
  if (!values.every(Number.isFinite)) throw Error('Nonfinite decoded accessor');
  const result = { type: a.type, count: a.count, values, decoded_sha256: hash(stable(values)) };
  g.cache.set(index, result); return result;
}
const matrix = node => node.matrix || new THREE.Matrix4().compose(new THREE.Vector3(...(node.translation || [0, 0, 0])), new THREE.Quaternion(...(node.rotation || [0, 0, 0, 1])), new THREE.Vector3(...(node.scale || [1, 1, 1]))).toArray();
function transformComponents(node) {
  const original = matrix(node);
  if (!original.every(Number.isFinite)) throw Error('Nonfinite local transform');
  let translation, rotation, scale;
  if (node.matrix) {
    const m = new THREE.Matrix4().fromArray(original), p = new THREE.Vector3(), q = new THREE.Quaternion(), s = new THREE.Vector3();
    m.decompose(p, q, s);
    translation = p.toArray(); rotation = q.toArray(); scale = s.toArray();
  } else {
    translation = node.translation || [0, 0, 0]; rotation = node.rotation || [0, 0, 0, 1]; scale = node.scale || [1, 1, 1];
  }
  if (![...translation, ...rotation, ...scale].every(Number.isFinite)) throw Error('Local transform decomposition is singular or nonfinite');
  const recomposed = new THREE.Matrix4().compose(new THREE.Vector3(...translation), new THREE.Quaternion(...rotation), new THREE.Vector3(...scale)).toArray();
  if (!equal(original, recomposed)) throw Error('Local matrix is not losslessly decomposable into TRS within the unchanged tolerance');
  return { translation, rotation, scale, representation: node.matrix ? 'matrix-decomposed-and-recomposed' : 'explicit-or-default-TRS' };
}
function differingTransformProperties(referenceNode, actualNode) {
  const reference = transformComponents(referenceNode), actual = transformComponents(actualNode), differences = [];
  for (const property of ['translation', 'rotation', 'scale']) {
    // q and -q are the same orientation. Compare rotation matrices while keeping
    // original component values in the report; all other tolerances are unchanged.
    const values = transform => property === 'rotation' ? new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion(...transform.rotation)).toArray() : transform[property];
    if (!equal(values(reference), values(actual))) differences.push({ property, reference: reference[property], actual: actual[property] });
  }
  if (!differences.length) throw Error('Different local matrices could not be classified into equivalent TRS components');
  return { differences, reference_representation: reference.representation, actual_representation: actual.representation };
}
function graph(g, referenceNames = null) {
  const nodes = g.doc.nodes || [], nameCounts = new Map();
  nodes.forEach(n => { if (n.name) nameCounts.set(n.name, (nameCounts.get(n.name) || 0) + 1); });
  let roots = [...(g.doc.scenes?.[g.doc.scene || 0]?.nodes || [])];
  const animated = new Set((g.doc.animations || []).flatMap(a => a.channels.map(c => c.target.node)));
  const ignored = [];
  while (roots.length === 1) {
    const index = roots[0], node = nodes[index];
    if ((node.children?.length || 0) !== 1 || node.mesh !== undefined || node.skin !== undefined || node.camera !== undefined || animated.has(index) || !equal(matrix(node), new THREE.Matrix4().toArray())) break;
    if (referenceNames ? referenceNames.has(node.name) : node.name) break;
    ignored.push({ index, name: node.name || null }); roots = [...node.children];
  }
  const byKey = new Map(), indexToKey = new Map();
  function walk(index, parentKey, ordinal, ancestors) {
    if (ancestors.has(index)) throw Error('Cycle in GLB hierarchy');
    if (indexToKey.has(index)) throw Error('Node has more than one parent/root instance');
    const node = nodes[index], key = node.name && nameCounts.get(node.name) === 1 ? 'name:' + node.name : `${parentKey || 'ROOT'}/child[${ordinal}]`;
    if (byKey.has(key)) throw Error('Ambiguous node key');
    indexToKey.set(index, key); byKey.set(key, { index, key, parent: parentKey, node });
    (node.children || []).forEach((child, i) => walk(child, key, i, new Set([...ancestors, index])));
  }
  roots.forEach((index, i) => walk(index, null, i, new Set()));
  return { byKey, indexToKey, ignored, names: new Set(nodes.map(n => n.name).filter(Boolean)), roots };
}
function material(g, index) {
  if (index === undefined) return null;
  const m = structuredClone(g.doc.materials[index]); delete m.name; delete m.extras;
  return m;
}
function primitives(g, node) {
  if (node.mesh === undefined) return [];
  return g.doc.meshes[node.mesh].primitives.map(p => {
    if (p.extensions?.KHR_draco_mesh_compression) throw Error('Compressed primitives unsupported');
    const attributes = Object.fromEntries(Object.entries(p.attributes).sort().map(([k, v]) => [k, accessor(g, v)]));
    const indices = p.indices === undefined ? null : accessor(g, p.indices);
    const targets = (p.targets || []).map(t => Object.fromEntries(Object.entries(t).sort().map(([k, v]) => [k, accessor(g, v)])));
    return { mode: p.mode ?? 4, material: material(g, p.material), attributes, indices, targets };
  });
}
function comparePrimitive(a, b) {
  const removeHashes = x => {
    if (Array.isArray(x)) return x.map(removeHashes);
    if (x && typeof x === 'object') return Object.fromEntries(Object.entries(x).filter(([k]) => k !== 'decoded_sha256').map(([k, v]) => [k, removeHashes(v)]));
    return x;
  };
  return equal(removeHashes(a), removeHashes(b));
}
function clips(g, gr) {
  const result = new Map();
  for (let i = 0; i < (g.doc.animations || []).length; i++) {
    const a = g.doc.animations[i], name = a.name || `clip[${i}]`;
    if (result.has(name)) throw Error('Duplicate clip names');
    const channels = a.channels.map(c => {
      const target = gr.indexToKey.get(c.target.node);
      if (!target) throw Error('Animation binds to missing/unreachable node');
      const s = a.samplers[c.sampler], input = accessor(g, s.input), output = accessor(g, s.output);
      const expected = c.target.path === 'rotation' ? 'VEC4' : ['translation', 'scale'].includes(c.target.path) ? 'VEC3' : null;
      if (!expected || input.type !== 'SCALAR' || output.type !== expected || output.count !== input.count * ((s.interpolation || 'LINEAR') === 'CUBICSPLINE' ? 3 : 1)) throw Error('Invalid track shape/binding');
      if (input.values.some((v, j) => j > 0 && v <= input.values[j - 1])) throw Error('Non-increasing track times');
      return { key: target + ':' + c.target.path, interpolation: s.interpolation || 'LINEAR', times: input.values, values: output.values, times_sha256: input.decoded_sha256, values_sha256: output.decoded_sha256 };
    }).sort((a, b) => a.key.localeCompare(b.key));
    if (new Set(channels.map(c => c.key)).size !== channels.length) throw Error('Duplicate channel binding in clip');
    result.set(name, channels);
  }
  return result;
}
async function samples(g, gr) {
  const buffer = g.bytes.buffer.slice(g.bytes.byteOffset, g.bytes.byteOffset + g.bytes.byteLength);
  const loaded = await new GLTFLoader().parseAsync(buffer, '');
  // Shared mesh instances may overwrite association records in r160; the node
  // dependency cache retains the actual distinct objects attached to the scene.
  const byNode = new Map(await Promise.all([...gr.indexToKey.keys()].map(async index => [index, await loaded.parser.getDependency('node', index)])));
  const initial = [];
  loaded.scene.traverse(o => initial.push([o, o.position.clone(), o.quaternion.clone(), o.scale.clone()]));
  const result = {};
  for (let i = 0; i < loaded.animations.length; i++) {
    const clip = loaded.animations[i];
    if (!(clip.duration > 0)) throw Error('Animation has no positive duration');
    for (const [o, p, q, s] of initial) { o.position.copy(p); o.quaternion.copy(q); o.scale.copy(s); }
    const mixer = new THREE.AnimationMixer(loaded.scene); mixer.clipAction(clip).play();
    const frames = [];
    // Non-quarter fractions avoid sampling a multi-turn rotor at identical poses.
    for (const fraction of [0, 0.137, 0.313, 0.617, 0.891]) {
      mixer.setTime(clip.duration * fraction); loaded.scene.updateMatrixWorld(true);
      frames.push(Object.fromEntries([...gr.byKey].map(([key, { index }]) => {
        const object = byNode.get(index); if (!object) throw Error('GLTFLoader node association missing: ' + key);
        return [key, object.matrixWorld.toArray()];
      })));
    }
    const changed = Object.keys(frames[0]).filter(key => frames.slice(1).some(f => !equal(frames[0][key], f[key])));
    result[clip.name || `clip[${i}]`] = { duration: clip.duration, fractions: [0, 0.137, 0.313, 0.617, 0.891], changed_nodes: changed.sort(), frames };
    mixer.stopAllAction(); mixer.uncacheRoot(loaded.scene);
  }
  return result;
}

try {
  const reference = parse(args.reference), actual = parse(args.actual);
  for (const [kind, g] of [['reference', reference], ['actual', actual]]) {
    report.inputs[kind] = { path: g.file, bytes: g.bytes.length, sha256: hash(g.bytes) };
    const v = await validator.validateBytes(new Uint8Array(g.bytes), { maxIssues: 100 });
    report.checks[kind + '_validator'] = { errors: v.issues.numErrors, warnings: v.issues.numWarnings, messages: v.issues.messages };
    if (v.issues.numErrors) fail('validator_errors', { input: kind, count: v.issues.numErrors });
  }
  const rg = graph(reference), ag = graph(actual, rg.names);
  report.checks.ignored_wrappers = { reference: rg.ignored, actual: ag.ignored };
  const rk = [...rg.byKey.keys()].sort(), ak = [...ag.byKey.keys()].sort();
  if (stable(rk) !== stable(ak)) fail('node_identity_set', { missing: rk.filter(k => !ag.byKey.has(k)), extra: ak.filter(k => !rg.byKey.has(k)) });
  const pendingPoseDifferences = [];
  const geometry = [], materialCounts = { reference: reference.doc.materials?.length || 0, actual: actual.doc.materials?.length || 0 };
  if (materialCounts.reference !== materialCounts.actual) report.warnings.push('Material definition count differs; every referenced primitive material is still compared.');
  for (const [key, r] of rg.byKey) {
    const a = ag.byKey.get(key); if (!a) continue;
    if (r.parent !== a.parent) fail('hierarchy_parent', { node: key, reference: r.parent, actual: a.parent });
    if (!equal(matrix(r.node), matrix(a.node))) {
      try { pendingPoseDifferences.push({ node: key, ...differingTransformProperties(r.node, a.node) }); }
      catch (error) { fail('local_transform_unclassifiable', { node: key, message: error.message, reference_matrix: matrix(r.node), actual_matrix: matrix(a.node) }); }
    }
    const rp = primitives(reference, r.node), ap = primitives(actual, a.node);
    if (!comparePrimitive(rp, ap)) fail('primitive_geometry_or_material', { node: key, reference_primitives: rp.length, actual_primitives: ap.length });
    geometry.push({ node: key, reference_primitives: rp.length, actual_primitives: ap.length,
      reference_decoded_sha256: hash(stable(rp)), actual_decoded_sha256: hash(stable(ap)), tolerant_match: comparePrimitive(rp, ap) });
  }
  report.checks.geometry = { reference_nodes: rg.byKey.size, actual_nodes: ag.byKey.size, reference_mesh_definitions: reference.doc.meshes?.length || 0, actual_mesh_definitions: actual.doc.meshes?.length || 0, material_counts: materialCounts, nodes: geometry };
  const rc = clips(reference, rg), ac = clips(actual, ag);
  const rnames = [...rc.keys()].sort(), anames = [...ac.keys()].sort();
  let allClipBindingsAndCurvesMatch = stable(rnames) === stable(anames);
  if (stable(rnames) !== stable(anames)) fail('clip_names', { reference: rnames, actual: anames });
  report.checks.animations = [];
  for (const [name, rchannels] of rc) {
    const achannels = ac.get(name) || [];
    const simple = channels => channels.map(({ times_sha256, values_sha256, ...rest }) => rest);
    const matched = equal(simple(rchannels), simple(achannels));
    allClipBindingsAndCurvesMatch = allClipBindingsAndCurvesMatch && matched;
    if (!matched) fail('clip_channels_or_curves', { clip: name, reference_channels: rchannels.length, actual_channels: achannels.length });
    report.checks.animations.push({ clip: name, matched, reference: rchannels.map(({ times, values, ...x }) => x), actual: achannels.map(({ times, values, ...x }) => x) });
  }
  const rs = await samples(reference, rg), as = await samples(actual, ag);
  report.checks.cpu_animation_samples = { matched: equal(rs, as), reference_clips: {}, actual_clips: {} };
  for (const [side, data] of [['reference_clips', rs], ['actual_clips', as]]) for (const [name, { frames, ...metadata }] of Object.entries(data)) report.checks.cpu_animation_samples[side][name] = { ...metadata, matrices_sha256: hash(stable(frames)) };
  if (!equal(rs, as)) fail('cpu_sampled_animation_world_matrices', {});
  for (const [name, data] of Object.entries(as)) if (!data.changed_nodes.length) fail('animation_did_not_move_at_samples', { clip: name });
  // Only now may a captured-pose difference be accepted. Every clip's exact
  // target/property binding and tolerant curve values, plus canonical world
  // samples, must match. A property on an animated node is not automatically
  // animated: translation, rotation and scale have separate permissions.
  const targetedProperties = new Map();
  for (const channels of rc.values()) for (const channel of channels) {
    const separator = channel.key.lastIndexOf(':'), node = channel.key.slice(0, separator), property = channel.key.slice(separator + 1);
    if (!targetedProperties.has(node)) targetedProperties.set(node, new Set());
    targetedProperties.get(node).add(property);
  }
  report.checks.captured_pose_differences = [];
  for (const candidate of pendingPoseDifferences) {
    const allowed = targetedProperties.get(candidate.node) || new Set();
    const untargeted = candidate.differences.filter(item => !allowed.has(item.property));
    const proof = { all_differing_properties_are_exact_animation_targets: untargeted.length === 0,
      matching_channel_properties: [...allowed].sort(), all_clip_bindings_and_curves_match: allClipBindingsAndCurvesMatch,
      canonical_world_samples_match: report.checks.cpu_animation_samples.matched,
      reference_and_actual_validator_errors_zero: report.checks.reference_validator.errors === 0 && report.checks.actual_validator.errors === 0 };
    const accepted = Object.entries(proof).filter(([key]) => key !== 'matching_channel_properties').every(([, value]) => value === true);
    report.checks.captured_pose_differences.push({ ...candidate, accepted, proof });
    if (accepted) report.warnings.push({ kind: 'captured_animated_pose_difference_accepted', ...candidate, proof });
    else fail(untargeted.length ? 'local_transform_unanimated_component' : 'local_transform_pose_proof_failed', { ...candidate, untargeted_properties: untargeted.map(item => item.property), proof });
  }
  report.status = report.failures.length ? 'FAIL' : 'PASS';
} catch (error) {
  fail('exception_or_unsupported_input', { message: String(error.message || error) });
}
fs.writeFileSync(args.out, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ status: report.status, report: args.out, failures: report.failures, warnings: report.warnings }));
process.exitCode = report.status === 'PASS' ? 0 : 1;
